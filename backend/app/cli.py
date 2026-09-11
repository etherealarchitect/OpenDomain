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
    opendomain transfer <domain> --auth-code <code>
    opendomain agent <message>
"""

import argparse
import json
import sys
from getpass import getpass

import httpx


DEFAULT_API = "http://localhost:8000/api/v1"


class OpenDomainCLI:
    def __init__(self, api_url: str = DEFAULT_API):
        self.api_url = api_url
        self.token: str | None = None
        self._load_token()

    def _load_token(self):
        try:
            with open(".opendomain-token") as f:
                self.token = f.read().strip()
        except FileNotFoundError:
            pass

    def _save_token(self, token: str):
        self.token = token
        with open(".opendomain-token", "w") as f:
            f.write(token)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
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
        result = self._request("POST", "/auth/login", {"email": email, "password": password})
        self._save_token(result["access_token"])
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
        print("Account created. You can now login.")

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
        result = self._request("POST", "/domains/transfer", {
            "domain": args.domain,
            "auth_code": args.auth_code,
            "registrant_contact_id": contacts[choice]["id"],
        })
        print(f"Transfer initiated: {result['status']}")

    def agent_chat(self, args):
        message = " ".join(args.message)
        result = self._request("POST", "/agent/chat", {"message": message})
        print(f"\n{result['response']}")
        if result.get("actions_taken"):
            print(f"\n  Actions: {len(result['actions_taken'])} tool(s) executed")


def main():
    parser = argparse.ArgumentParser(prog="opendomain", description="OpenDomain CLI")
    parser.add_argument("--api", default=DEFAULT_API, help="API base URL")
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
    transfer_p.add_argument("--auth-code", required=True)

    agent_p = sub.add_parser("agent", help="Chat with AI agent")
    agent_p.add_argument("message", nargs="+")

    args = parser.parse_args()
    cli = OpenDomainCLI(api_url=args.api)

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
        case _: parser.print_help()


if __name__ == "__main__":
    main()
