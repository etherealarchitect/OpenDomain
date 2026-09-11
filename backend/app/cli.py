"""
OpenDomain CLI — terminal interface for all platform operations.

Usage:
    opendomain login
    opendomain domains search <query>
    opendomain domains list
    opendomain domains register <domain>
    opendomain domains info <domain>
    opendomain domains renew <domain> [--years N]
    opendomain domains lock/unlock <domain>
    opendomain domains delete <domain>
    opendomain dns list <domain>
    opendomain dns add <domain> <type> <name> <content> [--ttl N] [--priority N]
    opendomain dns delete <domain> <record_id>
    opendomain dns export <domain>
    opendomain dns template <domain> <template_name> [--param key=value]
    opendomain contacts list
    opendomain contacts create
    opendomain whois <domain>
    opendomain transfer <domain>
    opendomain agent <message>
"""

import argparse
import hashlib
import os
import stat
import sys
import tempfile
from contextlib import suppress
from getpass import getpass
from pathlib import Path
from urllib.parse import urlsplit

import httpx

DEFAULT_API = "http://localhost:8000/api/v1"
STATE_DIR_ENV = "OPENDOMAIN_STATE_DIR"
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


def default_state_dir() -> Path:
    """Return a private, user-scoped state directory for CLI session data."""
    configured = os.environ.get(STATE_DIR_ENV)
    if configured:
        return Path(configured).expanduser()
    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    if xdg_state_home:
        return Path(xdg_state_home).expanduser() / "opendomain"
    return Path.home() / ".local" / "state" / "opendomain"


def _validate_api_url(api_url: str) -> str:
    """Require HTTPS, except for explicitly local development endpoints."""
    if not api_url or any(char.isspace() or ord(char) < 0x20 for char in api_url):
        raise ValueError("API URL must be an absolute HTTPS URL")
    normalized = api_url.rstrip("/")
    parsed = urlsplit(normalized)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("API URL must be an absolute HTTPS URL")
    if parsed.scheme == "http" and parsed.hostname.lower().rstrip(".") not in LOOPBACK_HOSTS:
        raise ValueError("API URL must use HTTPS (HTTP is only allowed for loopback development)")
    return normalized


def _reject_symlink_components(path: Path) -> None:
    """Reject symlinked components that could redirect credential storage."""
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OSError(f"Unsafe state directory: {current}")


def _ensure_private_directory(path: Path) -> None:
    """Create a private state directory and reject symlinked path components."""
    _reject_symlink_components(path)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    _reject_symlink_components(path)
    info = path.lstat()
    if info.st_mode & 0o077:
        raise OSError(f"State directory is too permissive: {path}")


class OpenDomainCLI:
    def __init__(self, api_url: str = DEFAULT_API, state_dir: Path | None = None):
        self.api_url = _validate_api_url(api_url)
        self.token: str | None = None
        root = state_dir or default_state_dir()
        origin = urlsplit(self.api_url)
        origin_key = f"{origin.scheme}://{origin.netloc}".encode()
        origin_digest = hashlib.sha256(origin_key).hexdigest()[:32]
        self.token_path = root / origin_digest / "session"
        self._load_token()

    def _load_token(self) -> None:
        _reject_symlink_components(self.token_path.parent)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        try:
            fd = os.open(self.token_path, flags)
        except (FileNotFoundError, OSError):
            return
        try:
            info = os.fstat(fd)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or info.st_mode & 0o077
            ):
                return
            self.token = os.read(fd, 1024 * 1024).decode("utf-8").strip() or None
        except (OSError, UnicodeDecodeError):
            self.token = None
        finally:
            os.close(fd)

    def _save_token(self, token: str) -> None:
        parent = self.token_path.parent
        _ensure_private_directory(parent)
        fd, temporary = tempfile.mkstemp(prefix=".session.", dir=parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                fd = -1
                file.write(token)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.token_path)
            self.token = token
        finally:
            if fd != -1:
                os.close(fd)
            with suppress(FileNotFoundError):
                os.unlink(temporary)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Cookie"] = f"opendomain_session={self.token}"
        return headers

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        url = f"{self.api_url}{path}"
        with httpx.Client(timeout=30) as client:
            resp = client.request(method, url, json=data, headers=self._headers())
            if resp.status_code == 401:
                print("Error: Not authenticated. Run 'opendomain login' first.")
                sys.exit(1)
            if resp.status_code >= 400:
                detail = resp.json().get("detail", resp.text)
                print(f"Error ({resp.status_code}): {detail}")
                sys.exit(1)
            if resp.status_code == 204:
                return {}
            return resp.json()

    def login(self, args):
        email = input("Email: ")
        password = getpass("Password: ")
        challenge = self._request("POST", "/auth/login", {"email": email, "password": password})
        if challenge["next_step"] == "mfa_enrollment":
            print("Authenticator enrollment is required. Complete setup in the web app first.")
            return
        code = getpass("Authenticator or recovery code: ")
        url = f"{self.api_url}/auth/mfa/verify"
        with httpx.Client(timeout=30) as client:
            response = client.post(
                url,
                json={"challenge_id": challenge["challenge_id"], "code": code},
                headers={"Content-Type": "application/json"},
            )
        if response.status_code >= 400:
            detail = response.json().get("detail", response.text)
            print(f"Error ({response.status_code}): {detail}")
            return
        session_cookie = response.cookies.get("opendomain_session")
        if not session_cookie:
            print("Error: Server did not establish a secure session.")
            return
        self._save_token(session_cookie)
        print("Logged in successfully.")

    def register_account(self, args):
        email = input("Email: ")
        full_name = input("Full name: ")
        password = getpass("Password: ")
        password2 = getpass("Confirm password: ")
        if password != password2:
            print("Passwords do not match.")
            sys.exit(1)
        self._request("POST", "/auth/register", {
            "email": email, "password": password, "full_name": full_name,
        })
        print("Check your email, verify the account, and complete authenticator setup in the web app.")

    def domains_search(self, args):
        result = self._request("POST", "/domains/search", {"query": args.query, "tlds": args.tlds})
        print(f"\n{'Domain':<30} {'Available':<12} {'Price':>10}")
        print("-" * 55)
        for r in result:
            avail = "YES" if r["available"] else "no"
            price = f"${r['price_cents'] / 100:.2f}/yr" if r["price_cents"] else "-"
            print(f"{r['domain']:<30} {avail:<12} {price:>10}")

    def domains_list(self, args):
        result = self._request("GET", "/domains/")
        if not result:
            print("No domains found.")
            return
        print(f"\n{'Domain':<30} {'Status':<15} {'Expires':<20} {'Auto-Renew':>10}")
        print("-" * 78)
        for d in result:
            print(f"{d['name']:<30} {d['status']:<15} {d['expiry_date'][:10]:<20} {'yes' if d['auto_renew'] else 'no':>10}")

    def domains_register(self, args):
        contacts = self._request("GET", "/contacts/")
        if not contacts:
            print("No contacts found. Create one first: opendomain contacts create")
            sys.exit(1)
        print("Select a contact:")
        for i, c in enumerate(contacts):
            print(f"  [{i + 1}] {c['label']} ({c['first_name']} {c['last_name']})")
        choice = int(input("Contact number: ")) - 1
        contact_id = contacts[choice]["id"]

        result = self._request("POST", "/domains/register", {
            "domain": args.domain,
            "period_years": args.years,
            "registrant_contact_id": contact_id,
            "privacy_enabled": not args.no_privacy,
            "auto_renew": not args.no_auto_renew,
        })
        print(f"\nRegistered: {result['name']}")
        print(f"  Status:  {result['status']}")
        print(f"  Expires: {result['expiry_date'][:10]}")
        print(f"  Price:   ${result['price_cents'] / 100:.2f}")

    def domains_info(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        print(f"\n  Domain:       {domain['name']}")
        print(f"  Status:       {domain['status']}")
        print(f"  TLD:          {domain['tld']}")
        print(f"  Registered:   {domain['registration_date'][:10]}")
        print(f"  Expires:      {domain['expiry_date'][:10]}")
        print(f"  Auto-renew:   {'yes' if domain['auto_renew'] else 'no'}")
        print(f"  Privacy:      {'on' if domain['privacy_enabled'] else 'off'}")
        print(f"  Locked:       {'yes' if domain['locked'] else 'no'}")
        print(f"  Nameservers:  {domain['nameservers']}")

    def domains_renew(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        result = self._request("POST", f"/domains/{domain['id']}/renew", {"period_years": args.years})
        print(f"Renewed {result['name']} — new expiry: {result['expiry_date'][:10]}")

    def domains_lock(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        action = "lock" if args.action == "lock" else "unlock"
        self._request("POST", f"/domains/{domain['id']}/{action}")
        print(f"Domain {args.domain} {'locked' if action == 'lock' else 'unlocked'}.")

    def domains_delete(self, args):
        confirm = input(f"Are you sure you want to delete {args.domain}? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        self._request("DELETE", f"/domains/{domain['id']}")
        print(f"Domain {args.domain} deletion initiated.")

    def dns_list(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        zone = self._request("GET", f"/domains/{domain['id']}/dns/")
        print(f"\nDNS Zone: {zone['zone_name']}  (serial: {zone['serial']})\n")
        print(f"{'Type':<8} {'Name':<20} {'Content':<40} {'TTL':>6} {'Pri':>5}")
        print("-" * 82)
        for r in zone.get("records", []):
            pri = str(r["priority"]) if r["priority"] is not None else ""
            print(f"{r['record_type']:<8} {r['name']:<20} {r['content']:<40} {r['ttl']:>6} {pri:>5}")

    def dns_add(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        data = {
            "record_type": args.type.upper(),
            "name": args.name,
            "content": args.content,
            "ttl": args.ttl,
        }
        if args.priority is not None:
            data["priority"] = args.priority
        result = self._request("POST", f"/domains/{domain['id']}/dns/records", data)
        print(f"Created {result['record_type']} record: {result['name']} -> {result['content']}")

    def dns_delete(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        self._request("DELETE", f"/domains/{domain['id']}/dns/records/{args.record_id}")
        print("Record deleted.")

    def dns_export(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        result = self._request("GET", f"/domains/{domain['id']}/dns/export")
        print(result["zone_file"])

    def dns_template(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        params = {}
        if args.param:
            for p in args.param:
                k, v = p.split("=", 1)
                params[k] = v
        self._request("POST", f"/domains/{domain['id']}/dns/templates", {
            "template": args.template_name, "params": params,
        })
        print(f"Applied '{args.template_name}' template to {args.domain}.")

    def contacts_list(self, args):
        result = self._request("GET", "/contacts/")
        if not result:
            print("No contacts found.")
            return
        print(f"\n{'ID':<38} {'Label':<20} {'Name':<25} {'Email':<30}")
        print("-" * 115)
        for c in result:
            print(f"{c['id']:<38} {c['label']:<20} {c['first_name']} {c['last_name']:<22} {c['email']:<30}")

    def contacts_create(self, args):
        data = {
            "label": input("Label (e.g., 'Personal'): "),
            "first_name": input("First name: "),
            "last_name": input("Last name: "),
            "organization": input("Organization (optional): ") or None,
            "email": input("Email: "),
            "phone": input("Phone (e.g., +1.5551234567): "),
            "address_line1": input("Address: "),
            "city": input("City: "),
            "state_province": input("State/Province: ") or None,
            "postal_code": input("Postal code: "),
            "country_code": input("Country code (e.g., US, AU): ").upper(),
        }
        result = self._request("POST", "/contacts/", data)
        print(f"Contact created: {result['id']}")

    def whois(self, args):
        result = self._request("POST", "/agent/chat", {
            "message": f"Do a WHOIS lookup on {args.domain}",
        })
        print(result["response"])

    def transfer(self, args):
        contacts = self._request("GET", "/contacts/")
        if not contacts:
            print("No contacts found. Create one first.")
            sys.exit(1)
        print("Select a contact for the transfer:")
        for i, c in enumerate(contacts):
            print(f"  [{i + 1}] {c['label']} ({c['first_name']} {c['last_name']})")
        choice = int(input("Contact number: ")) - 1
        auth_code = getpass("Transfer authorization code: ")
        result = self._request("POST", "/domains/transfer", {
            "domain": args.domain,
            "auth_code": auth_code,
            "registrant_contact_id": contacts[choice]["id"],
        })
        print(f"Transfer initiated: {result['status']}")

    def agent_chat(self, args):
        message = " ".join(args.message)
        result = self._request("POST", "/agent/chat", {"message": message})
        print(f"\n{result['response']}")
        if result.get("actions_taken"):
            print(f"\n  Actions: {len(result['actions_taken'])} tool(s) executed")

    # Monitoring
    def monitoring_alerts(self, args):
        result = self._request("GET", "/monitoring/alerts")
        if not result:
            print("No alerts.")
            return
        for a in result:
            status = "!" if a["status"] == "pending" else "."
            print(f"  [{status}] {a['alert_type']}: {a['title']} ({a['created_at'][:10]})")

    def monitoring_alerts_ack(self, args):
        self._request("POST", f"/monitoring/alerts/{args.alert_id}/acknowledge")
        print("Alert acknowledged.")

    def monitoring_watches_list(self, args):
        result = self._request("GET", "/monitoring/watches")
        if not result:
            print("No domain watches.")
            return
        for w in result:
            status = "AVAILABLE" if w["is_available"] else "taken"
            print(f"  {w['domain_name']:<30} {status}")

    def monitoring_watches_add(self, args):
        result = self._request("POST", "/monitoring/watches", {"query": args.domain})
        print(f"Watching {result['domain_name']}")

    def monitoring_uptime_list(self, args):
        result = self._request("GET", "/monitoring/uptime")
        if not result:
            print("No uptime checks.")
            return
        for c in result:
            rt = f"{c['response_time_ms']}ms" if c.get("response_time_ms") else "-"
            print(f"  {c['url']:<40} {c['status']:<8} {rt}")

    def monitoring_uptime_add(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        result = self._request("POST", "/monitoring/uptime", {"domain_id": domain["id"], "url": args.url})
        print(f"Uptime check created for {result['url']}")

    # Webhooks
    def webhooks_list(self, args):
        result = self._request("GET", "/webhooks/")
        if not result:
            print("No webhooks.")
            return
        for w in result:
            print(f"  {w['id'][:8]}  {w['url']:<50} failures={w['failure_count']}")

    def webhooks_create(self, args):
        result = self._request("POST", "/webhooks/", {"url": args.url, "events": args.events})
        print(f"Webhook created: {result['id']}")

    def webhooks_delete(self, args):
        self._request("DELETE", f"/webhooks/{args.id}")
        print("Webhook deleted.")

    # Marketplace
    def marketplace_browse(self, args):
        result = self._request("GET", "/marketplace/listings")
        if not result:
            print("No listings.")
            return
        for listing in result:
            name = listing.get("domain_name", listing["domain_id"][:8])
            print(
                f"  {name:<30} ${listing['asking_price_cents'] / 100:.2f}  "
                f"[{listing['status']}]"
            )

    def marketplace_create(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        self._request("POST", "/marketplace/listings", {
            "domain_id": domain["id"], "asking_price_cents": args.price,
        })
        print(f"Listed {args.domain} for ${args.price / 100:.2f}")

    # SSL
    def ssl_list(self, args):
        result = self._request("GET", "/ssl/certificates")
        if not result:
            print("No certificates.")
            return
        for c in result:
            print(f"  {c['domain_names']:<30} {c['status']:<12} expires={c.get('expires_at', '-')}")

    def ssl_request(self, args):
        domains = self._request("GET", "/domains/")
        domain = next((d for d in domains if d["name"] == args.domain.lower()), None)
        if not domain:
            print(f"Domain '{args.domain}' not found.")
            sys.exit(1)
        result = self._request("POST", "/ssl/certificates", {"domain_id": domain["id"]})
        print(f"Certificate requested: {result['status']}")

    # Billing
    def billing_invoices(self, args):
        result = self._request("GET", "/billing/invoices")
        if not result:
            print("No invoices.")
            return
        for i in result:
            print(f"  {i['invoice_number']:<15} {i['status']:<10} ${i['total_cents'] / 100:.2f}  {i['created_at'][:10]}")

    def billing_transactions(self, args):
        result = self._request("GET", "/billing/transactions")
        if not result:
            print("No transactions.")
            return
        for t in result:
            print(f"  {t['transaction_type']:<15} ${t['amount_cents'] / 100:.2f}  {t['description']}")

    # API Keys
    def api_keys_list(self, args):
        result = self._request("GET", "/api-keys/")
        if not result:
            print("No API keys.")
            return
        for k in result:
            print(f"  {k['prefix']}...  {k['name']:<20} {'active' if k['active'] else 'revoked'}")

    def api_keys_create(self, args):
        result = self._request("POST", "/api-keys/", {"name": args.name})
        print(f"API Key created: {result['key']}")
        print("  Save this key now — it won't be shown again.")

    def api_keys_revoke(self, args):
        self._request("DELETE", f"/api-keys/{args.id}")
        print("API key revoked.")

    # Bulk
    def bulk_renew(self, args):
        domains_list = self._request("GET", "/domains/")
        names = [n.strip().lower() for n in args.domains.split(",")]
        ids = [d["id"] for d in domains_list if d["name"] in names]
        result = self._request("POST", "/bulk/renew", {"domain_ids": ids, "years": args.years})
        print(f"Bulk renew: {result['succeeded']}/{result['total']} succeeded")


def main():
    parser = argparse.ArgumentParser(prog="opendomain", description="OpenDomain CLI")
    parser.add_argument("--api", default=DEFAULT_API, help="API base URL")
    parser.add_argument(
        "--state-dir",
        type=Path,
        help=f"Private CLI state directory (defaults to ${STATE_DIR_ENV} or XDG state)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("login", help="Login to OpenDomain")
    sub.add_parser("register", help="Create a new account")

    domains = sub.add_parser("domains", help="Domain management")
    dsub = domains.add_subparsers(dest="subcommand")

    search = dsub.add_parser("search", help="Search domains")
    search.add_argument("query")
    search.add_argument("--tlds", nargs="*")

    dsub.add_parser("list", help="List your domains")

    reg = dsub.add_parser("register", help="Register a domain")
    reg.add_argument("domain")
    reg.add_argument("--years", type=int, default=1)
    reg.add_argument("--no-privacy", action="store_true")
    reg.add_argument("--no-auto-renew", action="store_true")

    info = dsub.add_parser("info", help="Domain details")
    info.add_argument("domain")

    renew = dsub.add_parser("renew", help="Renew domain")
    renew.add_argument("domain")
    renew.add_argument("--years", type=int, default=1)

    for action in ("lock", "unlock"):
        p = dsub.add_parser(action, help=f"{action.title()} domain")
        p.add_argument("domain")

    delete = dsub.add_parser("delete", help="Delete domain")
    delete.add_argument("domain")

    dns_p = sub.add_parser("dns", help="DNS management")
    dns_sub = dns_p.add_subparsers(dest="subcommand")

    dns_list = dns_sub.add_parser("list", help="List DNS records")
    dns_list.add_argument("domain")

    dns_add = dns_sub.add_parser("add", help="Add DNS record")
    dns_add.add_argument("domain")
    dns_add.add_argument("type")
    dns_add.add_argument("name")
    dns_add.add_argument("content")
    dns_add.add_argument("--ttl", type=int, default=3600)
    dns_add.add_argument("--priority", type=int)

    dns_del = dns_sub.add_parser("delete", help="Delete DNS record")
    dns_del.add_argument("domain")
    dns_del.add_argument("record_id")

    dns_exp = dns_sub.add_parser("export", help="Export zone file")
    dns_exp.add_argument("domain")

    dns_tpl = dns_sub.add_parser("template", help="Apply DNS template")
    dns_tpl.add_argument("domain")
    dns_tpl.add_argument("template_name")
    dns_tpl.add_argument("--param", action="append")

    contacts_p = sub.add_parser("contacts", help="Contact management")
    contacts_sub = contacts_p.add_subparsers(dest="subcommand")
    contacts_sub.add_parser("list", help="List contacts")
    contacts_sub.add_parser("create", help="Create contact")

    whois_p = sub.add_parser("whois", help="WHOIS lookup")
    whois_p.add_argument("domain")

    transfer_p = sub.add_parser("transfer", help="Transfer domain in")
    transfer_p.add_argument("domain")

    agent_p = sub.add_parser("agent", help="Chat with AI agent")
    agent_p.add_argument("message", nargs="+")

    # Monitoring
    mon_p = sub.add_parser("monitoring", help="Monitoring & alerts")
    mon_sub = mon_p.add_subparsers(dest="subcommand")
    mon_sub.add_parser("alerts", help="List alerts")
    mon_ack = mon_sub.add_parser("ack", help="Acknowledge alert")
    mon_ack.add_argument("alert_id")
    mon_sub.add_parser("watches", help="List domain watches")
    mon_wa = mon_sub.add_parser("watch", help="Add domain watch")
    mon_wa.add_argument("domain")
    mon_sub.add_parser("uptime", help="List uptime checks")
    mon_ua = mon_sub.add_parser("uptime-add", help="Add uptime check")
    mon_ua.add_argument("domain")
    mon_ua.add_argument("url")

    # Webhooks
    wh_p = sub.add_parser("webhooks", help="Webhook management")
    wh_sub = wh_p.add_subparsers(dest="subcommand")
    wh_sub.add_parser("list", help="List webhooks")
    wh_create = wh_sub.add_parser("create", help="Create webhook")
    wh_create.add_argument("url")
    wh_create.add_argument("--events", nargs="+", required=True)
    wh_del = wh_sub.add_parser("delete", help="Delete webhook")
    wh_del.add_argument("id")

    # Marketplace
    mp_p = sub.add_parser("marketplace", help="Domain marketplace")
    mp_sub = mp_p.add_subparsers(dest="subcommand")
    mp_sub.add_parser("browse", help="Browse listings")
    mp_create = mp_sub.add_parser("create", help="List domain for sale")
    mp_create.add_argument("domain")
    mp_create.add_argument("--price", type=int, required=True, help="Price in cents")

    # SSL
    ssl_p = sub.add_parser("ssl", help="SSL certificate management")
    ssl_sub = ssl_p.add_subparsers(dest="subcommand")
    ssl_sub.add_parser("list", help="List certificates")
    ssl_req = ssl_sub.add_parser("request", help="Request certificate")
    ssl_req.add_argument("domain")

    # Billing
    bill_p = sub.add_parser("billing", help="Billing & invoices")
    bill_sub = bill_p.add_subparsers(dest="subcommand")
    bill_sub.add_parser("invoices", help="List invoices")
    bill_sub.add_parser("transactions", help="List transactions")

    # API Keys
    ak_p = sub.add_parser("api-keys", help="API key management")
    ak_sub = ak_p.add_subparsers(dest="subcommand")
    ak_sub.add_parser("list", help="List API keys")
    ak_create = ak_sub.add_parser("create", help="Create API key")
    ak_create.add_argument("name")
    ak_rev = ak_sub.add_parser("revoke", help="Revoke API key")
    ak_rev.add_argument("id")

    # Bulk
    bulk_p = sub.add_parser("bulk", help="Bulk operations")
    bulk_sub = bulk_p.add_subparsers(dest="subcommand")
    bulk_renew_p = bulk_sub.add_parser("renew", help="Bulk renew domains")
    bulk_renew_p.add_argument("--domains", required=True, help="Comma-separated domain names")
    bulk_renew_p.add_argument("--years", type=int, default=1)

    args = parser.parse_args()
    cli = OpenDomainCLI(api_url=args.api, state_dir=args.state_dir)

    match args.command:
        case "login": cli.login(args)
        case "register": cli.register_account(args)
        case "domains":
            match args.subcommand:
                case "search": cli.domains_search(args)
                case "list": cli.domains_list(args)
                case "register": cli.domains_register(args)
                case "info": cli.domains_info(args)
                case "renew": cli.domains_renew(args)
                case "lock" | "unlock":
                    args.action = args.subcommand
                    cli.domains_lock(args)
                case "delete": cli.domains_delete(args)
                case _: domains.print_help()
        case "dns":
            match args.subcommand:
                case "list": cli.dns_list(args)
                case "add": cli.dns_add(args)
                case "delete": cli.dns_delete(args)
                case "export": cli.dns_export(args)
                case "template": cli.dns_template(args)
                case _: dns_p.print_help()
        case "contacts":
            match args.subcommand:
                case "list": cli.contacts_list(args)
                case "create": cli.contacts_create(args)
                case _: contacts_p.print_help()
        case "whois": cli.whois(args)
        case "transfer": cli.transfer(args)
        case "agent": cli.agent_chat(args)
        case "monitoring":
            match args.subcommand:
                case "alerts": cli.monitoring_alerts(args)
                case "ack": cli.monitoring_alerts_ack(args)
                case "watches": cli.monitoring_watches_list(args)
                case "watch": cli.monitoring_watches_add(args)
                case "uptime": cli.monitoring_uptime_list(args)
                case "uptime-add": cli.monitoring_uptime_add(args)
                case _: mon_p.print_help()
        case "webhooks":
            match args.subcommand:
                case "list": cli.webhooks_list(args)
                case "create": cli.webhooks_create(args)
                case "delete": cli.webhooks_delete(args)
                case _: wh_p.print_help()
        case "marketplace":
            match args.subcommand:
                case "browse": cli.marketplace_browse(args)
                case "create": cli.marketplace_create(args)
                case _: mp_p.print_help()
        case "ssl":
            match args.subcommand:
                case "list": cli.ssl_list(args)
                case "request": cli.ssl_request(args)
                case _: ssl_p.print_help()
        case "billing":
            match args.subcommand:
                case "invoices": cli.billing_invoices(args)
                case "transactions": cli.billing_transactions(args)
                case _: bill_p.print_help()
        case "api-keys":
            match args.subcommand:
                case "list": cli.api_keys_list(args)
                case "create": cli.api_keys_create(args)
                case "revoke": cli.api_keys_revoke(args)
                case _: ak_p.print_help()
        case "bulk":
            match args.subcommand:
                case "renew": cli.bulk_renew(args)
                case _: bulk_p.print_help()
        case _: parser.print_help()


if __name__ == "__main__":
    main()
