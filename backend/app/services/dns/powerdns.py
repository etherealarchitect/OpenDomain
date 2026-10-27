"""PowerDNS authoritative provider client.

OpenDomain keeps zone data in PostgreSQL and publishes it to the configured
authoritative DNS server. This module is the PowerDNS implementation of that
provider seam: it turns application zone/record rows into PowerDNS RRsets and
pushes them over the PowerDNS HTTP API.

Publishing is only attempted when a provider is configured
(``DNS_PROVIDER=powerdns``); see :func:`backend.app.services.dns.get_dns_provider`.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

import httpx

from backend.app.core.config import settings
from backend.app.models.dns import DnsRecord, DnsZone, RecordType

logger = logging.getLogger(__name__)

# PowerDNS serves zones as "Native" unless a real replication setup manages them.
ZONE_KIND = "Native"

# RRsets PowerDNS owns itself after DNSSEC is enabled; never delete them.
PROVIDER_MANAGED_TYPES = {"RRSIG", "NSEC", "NSEC3", "NSEC3PARAM", "DNSKEY", "CDNSKEY", "CDS"}

# Record types whose content is a domain name and therefore needs an absolute target.
_NAME_TARGET_TYPES = {"CNAME", "NS", "PTR", "ALIAS", "MX", "SRV"}

_PRIORITY_PREFIXED_TYPES = {"MX", "SRV"}


class DnsProviderError(RuntimeError):
    """Raised when the authoritative provider rejects or cannot serve a change."""


def zone_id(zone_name: str) -> str:
    """Return the PowerDNS zone identifier (the zone name with a trailing dot)."""
    return f"{zone_name.rstrip('.')}."


def absolute_name(name: str, zone_name: str) -> str:
    """Resolve a zone-relative record name (``@``, ``www``) to a fully qualified name."""
    zone = zone_id(zone_name)
    candidate = name.strip()
    if candidate in ("", "@"):
        return zone
    candidate = candidate.rstrip(".")
    if candidate == zone.rstrip(".") or candidate.endswith(f".{zone.rstrip('.')}"):
        return f"{candidate}."
    return f"{candidate}.{zone}"


def _absolute_target(value: str, zone_name: str) -> str:
    target = value.strip().rstrip(".")
    if target == "@":
        return zone_id(zone_name)
    if target.endswith(f".{zone_name.rstrip('.')}"):
        return f"{target}."
    return f"{target}."


def _record_content(record: DnsRecord, zone_name: str) -> str:
    content = record.content.strip()
    record_type = record.record_type

    if record_type in _PRIORITY_PREFIXED_TYPES:
        parts = content.split()
        if record_type == "MX":
            target = parts[-1] if parts else content
            return f"{record.priority or 0} {_absolute_target(target, zone_name)}"
        if len(parts) >= 3:
            weight, port, target = parts[-3], parts[-2], parts[-1]
            return f"{record.priority or 0} {weight} {port} {_absolute_target(target, zone_name)}"
        return f"{record.priority or 0} {content}"

    if record_type == "TXT":
        if content.startswith('"') and content.endswith('"'):
            return content
        escaped = content.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    if record_type in _NAME_TARGET_TYPES:
        return _absolute_target(content, zone_name)

    return content


def _soa_content(zone: DnsZone) -> str:
    admin = zone.admin_email.replace("@", ".")
    if not admin.endswith("."):
        admin = f"{admin}."
    return (
        f"{zone.primary_ns.rstrip('.')}. {admin} {zone.serial} "
        f"{zone.refresh} {zone.retry} {zone.expire} {zone.minimum_ttl}"
    )


def build_rrsets(zone: DnsZone, records: Sequence[DnsRecord]) -> list[dict[str, Any]]:
    """Group application records into PowerDNS RRsets (apex SOA included)."""
    grouped: dict[tuple[str, str], dict[str, Any]] = {}

    def add(name: str, record_type: str, content: str, ttl: int) -> None:
        key = (name, record_type)
        rrset = grouped.setdefault(
            key, {"name": name, "type": record_type, "ttl": ttl, "changetype": "REPLACE", "records": []}
        )
        rrset["ttl"] = min(rrset["ttl"], ttl)
        rrset["records"].append({"content": content, "disabled": False})

    add(zone_id(zone.zone_name), "SOA", _soa_content(zone), zone.default_ttl)
    for record in records:
        if not record.enabled or record.record_type in (RecordType.SOA, RecordType.DNSKEY):
            continue
        add(
            absolute_name(record.name, zone.zone_name),
            str(record.record_type),
            _record_content(record, zone.zone_name),
            record.ttl or zone.default_ttl,
        )

    return list(grouped.values())


class PowerDnsProvider:
    """Minimal PowerDNS HTTP API client for zone publishing."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        server_id: str = "localhost",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = (base_url or settings.powerdns_api_url).rstrip("/")
        self.api_key = api_key or settings.powerdns_api_key
        self.server_id = server_id
        self.timeout = timeout

    async def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> httpx.Response:
        url = f"{self.base_url}/api/v1/servers/{self.server_id}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method, url, json=payload, headers={"X-API-Key": self.api_key}
                )
        except httpx.HTTPError as exc:
            raise DnsProviderError(f"cannot reach the DNS provider at {self.base_url}") from exc

        if response.status_code >= 400:
            detail = response.text.strip()[:300]
            raise DnsProviderError(
                f"DNS provider rejected {method} {path}: {response.status_code} {detail}"
            )
        return response

    async def get_zone(self, zone_name: str) -> dict[str, Any] | None:
        url = f"{self.base_url}/api/v1/servers/{self.server_id}/zones/{zone_id(zone_name)}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers={"X-API-Key": self.api_key})
        except httpx.HTTPError as exc:
            raise DnsProviderError(f"cannot reach the DNS provider at {self.base_url}") from exc

        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise DnsProviderError(
                f"DNS provider rejected GET zone {zone_name}: {response.status_code}"
            )
        return response.json()

    def _nameservers(self, zone: DnsZone, records: Sequence[DnsRecord]) -> list[str]:
        servers = {
            absolute_name(record.content, zone.zone_name)
            for record in records
            if record.record_type == RecordType.NS and record.enabled
        }
        if not servers:
            servers = {f"{zone.primary_ns.rstrip('.')}."}
        return sorted(servers)

    async def create_zone(self, zone: DnsZone, records: Sequence[DnsRecord]) -> None:
        await self._request(
            "POST",
            "/zones",
            {
                "name": zone_id(zone.zone_name),
                "kind": ZONE_KIND,
                "nameservers": self._nameservers(zone, records),
            },
        )

    async def delete_zone(self, zone_name: str) -> None:
        await self._request("DELETE", f"/zones/{zone_id(zone_name)}")

    async def sync_zone(self, zone: DnsZone, records: Sequence[DnsRecord]) -> None:
        """Make the provider's copy of the zone match the application's records."""
        existing = await self.get_zone(zone.zone_name)
        if existing is None:
            await self.create_zone(zone, records)

        desired = build_rrsets(zone, records)
        desired_keys = {(rrset["name"], rrset["type"]) for rrset in desired}
        changes: list[dict[str, Any]] = list(desired)

        for rrset in (existing or {}).get("rrsets", []):
            key = (rrset["name"], rrset["type"])
            if rrset["type"] in PROVIDER_MANAGED_TYPES or key in desired_keys:
                continue
            changes.append({"name": key[0], "type": key[1], "changetype": "DELETE"})

        await self._request("PATCH", f"/zones/{zone_id(zone.zone_name)}", {"rrsets": changes})

    async def set_dnssec(self, zone_name: str, enabled: bool) -> str | None:
        """Toggle DNSSEC signing and return the DS record to publish in the parent zone."""
        await self._request(
            "PUT",
            f"/zones/{zone_id(zone_name)}",
            {"name": zone_id(zone_name), "kind": ZONE_KIND, "dnssec": enabled},
        )
        if not enabled:
            return None
        return await self._active_ds_record(zone_name)

    async def rotate_dnssec_key(self, zone_name: str) -> str | None:
        """Create a fresh signing key, retire the superseded ones, return the new DS."""
        await self._request(
            "POST", f"/zones/{zone_id(zone_name)}/cryptokeys", {"keytype": "csk", "active": True}
        )
        response = await self._request("GET", f"/zones/{zone_id(zone_name)}/cryptokeys")
        keys = response.json()
        if not keys:
            logger.warning("PowerDNS reported no signing keys for %s after rotation", zone_name)
            return None

        newest = max(keys, key=lambda key: key.get("id", 0))
        for key in keys:
            if key.get("id") == newest.get("id") or key.get("active", True):
                continue
            await self._request(
                "DELETE", f"/zones/{zone_id(zone_name)}/cryptokeys/{key.get('id')}"
            )
        return self._ds_record(newest, zone_name)

    async def _active_ds_record(self, zone_name: str) -> str | None:
        response = await self._request("GET", f"/zones/{zone_id(zone_name)}/cryptokeys")
        for key in response.json():
            if key.get("active", True):
                ds_record = self._ds_record(key, zone_name)
                if ds_record:
                    return ds_record
        logger.warning("PowerDNS returned no DS record for %s", zone_name)
        return None

    @staticmethod
    def _ds_record(key: dict[str, Any], zone_name: str) -> str | None:
        ds_records = key.get("ds") or []
        if not ds_records:
            logger.warning("PowerDNS returned no DS record for %s", zone_name)
            return None
        return str(ds_records[0])
