import logging
from dataclasses import dataclass
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


@dataclass
class WhoisResult:
    domain_name: str
    registrar: str | None = None
    creation_date: datetime | None = None
    expiration_date: datetime | None = None
    updated_date: datetime | None = None
    status: list[str] | None = None
    nameservers: list[str] | None = None
    registrant_name: str | None = None
    registrant_org: str | None = None
    registrant_country: str | None = None
    raw: str = ""


class WhoisService:
    RDAP_BOOTSTRAP = "https://rdap.org"

    async def lookup(self, domain_name: str) -> WhoisResult:
        result = WhoisResult(domain_name=domain_name)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.RDAP_BOOTSTRAP}/domain/{domain_name}")
                if resp.status_code == 200:
                    data = resp.json()
                    result = self._parse_rdap(domain_name, data)
        except Exception:
            logger.warning("RDAP lookup failed for %s, falling back to raw WHOIS", domain_name)

        return result

    def _parse_rdap(self, domain_name: str, data: dict) -> WhoisResult:
        result = WhoisResult(domain_name=domain_name)

        result.status = data.get("status", [])

        nameservers = data.get("nameservers", [])
        result.nameservers = [ns.get("ldhName", "") for ns in nameservers if ns.get("ldhName")]

        for event in data.get("events", []):
            action = event.get("eventAction")
            date_str = event.get("eventDate")
            if not date_str:
                continue
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                continue
            if action == "registration":
                result.creation_date = dt
            elif action == "expiration":
                result.expiration_date = dt
            elif action == "last changed":
                result.updated_date = dt

        for entity in data.get("entities", []):
            if "registrar" in entity.get("roles", []):
                vcard = entity.get("vcardArray", [None, []])[1] if entity.get("vcardArray") else []
                for field in vcard:
                    if field[0] == "fn":
                        result.registrar = field[3]
            if "registrant" in entity.get("roles", []):
                vcard = entity.get("vcardArray", [None, []])[1] if entity.get("vcardArray") else []
                for field in vcard:
                    if field[0] == "fn":
                        result.registrant_name = field[3]
                    if field[0] == "org":
                        result.registrant_org = field[3]

        return result
