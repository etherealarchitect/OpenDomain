import asyncio
import ipaddress
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from urllib.parse import urljoin, urlparse

import httpx
import whois

logger = logging.getLogger(__name__)


@dataclass
class WhoisResult:
    domain_name: str
    lookup_status: Literal["registered", "not_found", "available", "unknown"] = "unknown"
    source: Literal["rdap", "whois", "none"] = "none"
    registrar: str | None = None
    creation_date: datetime | None = None
    expiration_date: datetime | None = None
    updated_date: datetime | None = None
    status: list[str] = field(default_factory=list)
    nameservers: list[str] = field(default_factory=list)
    dnssec: bool | None = None
    registrant_name: str | None = None
    registrant_org: str | None = None
    registrant_country: str | None = None
    warnings: list[str] = field(default_factory=list)


class WhoisService:
    RDAP_BOOTSTRAP = "https://rdap.org"
    TRUSTED_RDAP_HOSTS = {
        "rdap.org",
        "rdap.verisign.com",
        "rdap.publicinterestregistry.org",
    }
    RDAP_DEADLINE_SECONDS = 10.0
    CACHE_TTL = timedelta(minutes=5)
    MAX_CACHE_ENTRIES = 1_000
    MAX_RDAP_BYTES = 1_048_576
    MAX_REDIRECTS = 2
    MAX_CONCURRENT_LOOKUPS = 10
    RDAP_TIMEOUT = httpx.Timeout(8.0, connect=3.0)
    WHOIS_TIMEOUT_SECONDS = 8.0
    _label_re = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)

    def __init__(self) -> None:
        self._cache: dict[str, tuple[datetime, WhoisResult]] = {}
        self._cache_lock = asyncio.Lock()
        self._network_limit = asyncio.Semaphore(self.MAX_CONCURRENT_LOOKUPS)

    async def lookup(self, domain_name: str) -> WhoisResult:
        normalized = self.normalize_domain(domain_name)
        now = datetime.now(UTC)
        async with self._cache_lock:
            cached = self._cache.get(normalized)
            if cached and cached[0] > now:
                return cached[1]
            if cached:
                self._cache.pop(normalized, None)

        async with self._network_limit:
            result = await self._lookup_rdap(normalized)
            # Do not invoke python-whois automatically: its synchronous client
            # can follow registry referrals and a timed-out worker continues in
            # the executor. RDAP failures therefore remain explicitly unknown.

        async with self._cache_lock:
            self._cache[normalized] = (datetime.now(UTC) + self.CACHE_TTL, result)
            self._prune_cache(self._cache, datetime.now(UTC))
        return result

    @classmethod
    def normalize_domain(cls, domain_name: str) -> str:
        if not isinstance(domain_name, str) or any(
            ord(char) < 32 or ord(char) == 127 for char in domain_name
        ):
            raise ValueError("Enter a valid fully qualified domain name")
        candidate = domain_name.strip().rstrip(".").lower()
        # URLs, user-info, ports, paths, and whitespace are never domain names.
        if (
            not candidate
            or any(char.isspace() for char in candidate)
            or any(char in candidate for char in "/\\:@?#%")
            or "." not in candidate
        ):
            raise ValueError("Enter a valid fully qualified domain name")
        try:
            normalized = candidate.encode("idna").decode("ascii")
        except (UnicodeError, UnicodeEncodeError) as exc:
            raise ValueError("Enter a valid internationalized domain name") from exc
        if len(normalized) > 253:
            raise ValueError("Enter a valid fully qualified domain name")
        try:
            if ipaddress.ip_address(normalized):
                raise ValueError("IP addresses are not valid domain names")
        except ValueError as exc:
            if str(exc) == "IP addresses are not valid domain names":
                raise
        labels = normalized.split(".")
        if len(labels) < 2 or any(
            not label or len(label) > 63 or not cls._label_re.fullmatch(label) for label in labels
        ):
            raise ValueError("Enter a valid fully qualified domain name")
        return normalized

    def _prune_cache(
        self, cache: dict[str, tuple[datetime, WhoisResult]] | Any, now: datetime | None = None
    ) -> None:
        now = now or datetime.now(UTC)
        expired = [key for key, (expires, _) in cache.items() if expires <= now]
        for key in expired:
            cache.pop(key, None)
        # Dicts preserve insertion order; dropping oldest entries gives a bounded cache.
        while len(cache) > self.MAX_CACHE_ENTRIES:
            cache.pop(next(iter(cache)))

    async def _lookup_rdap(self, domain_name: str) -> WhoisResult:
        url = f"{self.RDAP_BOOTSTRAP}/domain/{domain_name}"
        try:
            async with asyncio.timeout(self.RDAP_DEADLINE_SECONDS):
                async with httpx.AsyncClient(
                    timeout=self.RDAP_TIMEOUT, follow_redirects=False
                ) as client:
                    for _ in range(self.MAX_REDIRECTS + 1):
                        async with client.stream(
                            "GET", url, headers={"Accept": "application/rdap+json, application/json"}
                        ) as response:
                            if response.status_code == 404:
                                return WhoisResult(
                                    domain_name=domain_name, lookup_status="not_found", source="rdap",
                                    warnings=["RDAP did not find a registration; registrability was not established."],
                                )
                            if response.is_redirect:
                                location = response.headers.get("location")
                                safe_url = self._safe_redirect(url, location, domain_name)
                                if safe_url is None:
                                    return WhoisResult(
                                        domain_name=domain_name,
                                        warnings=["RDAP returned an unsafe redirect; lookup stopped."],
                                    )
                                url = safe_url
                                continue
                            response.raise_for_status()
                            body = bytearray()
                            async for chunk in response.aiter_bytes():
                                body.extend(chunk)
                                if len(body) > self.MAX_RDAP_BYTES:
                                    raise ValueError("RDAP response exceeded size limit")
                            data = httpx.Response(response.status_code, content=bytes(body)).json()
                            return self._parse_rdap(domain_name, data)
                return WhoisResult(
                    domain_name=domain_name,
                    warnings=["RDAP returned too many redirects; lookup stopped."],
                )
        except (httpx.HTTPError, ValueError, TypeError, UnicodeError) as exc:
            logger.info("RDAP lookup unavailable for %s: %s", domain_name, type(exc).__name__)
            return WhoisResult(
                domain_name=domain_name,
                warnings=["RDAP lookup was temporarily unavailable; automatic WHOIS fallback is disabled for safety."],
            )

    @classmethod
    def _safe_redirect(cls, current_url: str, location: str | None, domain_name: str) -> str | None:
        if not location:
            return None
        parsed = urlparse(urljoin(current_url, location))
        if (
            parsed.scheme != "https"
            or parsed.username
            or parsed.password
            or parsed.fragment
            or parsed.query
            or parsed.port not in (None, 443)
        ):
            return None
        host = parsed.hostname
        if not host or host != host.lower() or host not in cls.TRUSTED_RDAP_HOSTS:
            return None
        try:
            address = ipaddress.ip_address(host)
            if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
                return None
        except ValueError:
            pass
        path = parsed.path.rstrip("/")
        expected_paths = {f"/domain/{domain_name}", f"/com/v1/domain/{domain_name}"}
        if path not in expected_paths:
            return None
        return parsed.geturl()

    async def _lookup_whois(self, domain_name: str) -> WhoisResult:
        # Deliberately disabled: python-whois may follow untrusted referrals and
        # cannot cancel its underlying blocking thread on timeout.
        return WhoisResult(
            domain_name=domain_name,
            warnings=["WHOIS fallback is disabled because referral requests cannot be safely bounded."],
        )

    async def _unsafe_lookup_whois_removed(self, domain_name: str) -> WhoisResult:
        try:
            record = await asyncio.wait_for(
                asyncio.to_thread(whois.whois, domain_name), self.WHOIS_TIMEOUT_SECONDS
            )
        except (TimeoutError, Exception) as exc:
            logger.info("WHOIS fallback unavailable for %s: %s", domain_name, type(exc).__name__)
            return WhoisResult(
                domain_name=domain_name, warnings=["WHOIS fallback was temporarily unavailable."]
            )

        registrar = self._first(getattr(record, "registrar", None))
        nameservers = sorted(
            {
                str(value).lower().rstrip(".")
                for value in self._as_list(getattr(record, "name_servers", None))
                if value
            }
        )
        domain_name_value = self._first(getattr(record, "domain_name", None))
        registered = bool(domain_name_value or registrar or nameservers)
        return WhoisResult(
            domain_name=domain_name,
            lookup_status="registered" if registered else "unknown",
            source="whois",
            registrar=registrar,
            creation_date=self._first_datetime(getattr(record, "creation_date", None)),
            expiration_date=self._first_datetime(getattr(record, "expiration_date", None)),
            updated_date=self._first_datetime(getattr(record, "updated_date", None)),
            status=[
                str(value) for value in self._as_list(getattr(record, "status", None)) if value
            ],
            nameservers=nameservers,
            dnssec=self._dnssec(getattr(record, "dnssec", None)),
            registrant_name=self._first(getattr(record, "name", None)),
            registrant_org=self._first(getattr(record, "org", None)),
            registrant_country=self._first(getattr(record, "country", None)),
        )

    @staticmethod
    def _as_list(value: object) -> list[object]:
        return value if isinstance(value, list) else ([] if value is None else [value])

    @classmethod
    def _first(cls, value: object) -> str | None:
        values = cls._as_list(value)
        return str(values[0]) if values and values[0] else None

    @classmethod
    def _first_datetime(cls, value: object) -> datetime | None:
        values = cls._as_list(value)
        return values[0] if values and isinstance(values[0], datetime) else None

    @staticmethod
    def _dnssec(value: object) -> bool | None:
        if value is None:
            return None
        return str(value).strip().lower() in {"signed", "yes", "true", "1"}

    def _parse_rdap(self, domain_name: str, data: object) -> WhoisResult:
        if not isinstance(data, dict):
            raise ValueError("Malformed RDAP payload")
        for key in ("status", "nameservers", "events", "entities"):
            if key in data and not isinstance(data[key], list):
                raise ValueError("Malformed RDAP payload")
        result = WhoisResult(domain_name=domain_name, lookup_status="registered", source="rdap")
        statuses = data.get("status", [])
        result.status = [str(value) for value in statuses] if isinstance(statuses, list) else []
        secure_dns = data.get("secureDNS")
        if isinstance(secure_dns, dict) and isinstance(secure_dns.get("delegationSigned"), bool):
            result.dnssec = secure_dns["delegationSigned"]
        nameservers = data.get("nameservers", [])
        if isinstance(nameservers, list):
            result.nameservers = [
                str(ns["ldhName"]).lower().rstrip(".")
                for ns in nameservers
                if isinstance(ns, dict) and ns.get("ldhName")
            ]
        events = data.get("events", [])
        if isinstance(events, list):
            for event in events:
                if not isinstance(event, dict) or not isinstance(event.get("eventDate"), str):
                    continue
                try:
                    dt = datetime.fromisoformat(event["eventDate"].replace("Z", "+00:00"))
                except ValueError:
                    continue
                if event.get("eventAction") == "registration":
                    result.creation_date = dt
                elif event.get("eventAction") == "expiration":
                    result.expiration_date = dt
                elif event.get("eventAction") == "last changed":
                    result.updated_date = dt
        entities = data.get("entities", [])
        if isinstance(entities, list):
            for entity in entities:
                if not isinstance(entity, dict) or not isinstance(entity.get("roles"), list):
                    continue
                vcard = entity.get("vcardArray")
                fields = (
                    vcard[1]
                    if isinstance(vcard, list) and len(vcard) > 1 and isinstance(vcard[1], list)
                    else []
                )
                for field in fields:
                    if (
                        not isinstance(field, list)
                        or len(field) < 4
                        or not isinstance(field[0], str)
                    ):
                        continue
                    if "registrar" in entity["roles"] and field[0] == "fn":
                        result.registrar = str(field[3])
                    if "registrant" in entity["roles"]:
                        if field[0] == "fn":
                            result.registrant_name = str(field[3])
                        elif field[0] == "org":
                            result.registrant_org = str(field[3])
                        elif field[0] == "adr" and isinstance(field[3], list):
                            result.registrant_country = next(
                                (str(value) for value in reversed(field[3]) if value), None
                            )
        return result
