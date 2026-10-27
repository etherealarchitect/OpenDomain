"""DNS provider integration.

Zone data lives in PostgreSQL and is published to the authoritative nameservers by
the configured provider (``DNS_PROVIDER``). ``powerdns`` selects the PowerDNS
implementation in :mod:`backend.app.services.dns.powerdns`; any other value keeps
the platform in application-only mode, where zone data is stored but not served.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.dns import DnsRecord, DnsZone
from backend.app.services.dns.powerdns import (
    DnsProviderError,
    PowerDnsProvider,
    absolute_name,
    build_rrsets,
    zone_id,
)

__all__ = [
    "DnsProviderError",
    "PowerDnsProvider",
    "absolute_name",
    "build_rrsets",
    "get_dns_provider",
    "publish_zone",
    "zone_id",
]


def get_dns_provider() -> PowerDnsProvider | None:
    """Return the configured authoritative provider, or None for zone-data-only mode."""
    if settings.dns_provider.strip().lower() != "powerdns":
        return None
    return PowerDnsProvider()


async def publish_zone(db: AsyncSession, zone: DnsZone) -> None:
    """Publish the zone and its records to the provider.

    No-op when no provider is configured. Provider failures raise
    :class:`DnsProviderError`, which rolls the caller's transaction back so stored
    zone data never drifts from what the nameservers serve.
    """
    provider = get_dns_provider()
    if provider is None:
        return

    result = await db.execute(select(DnsRecord).where(DnsRecord.zone_id == zone.id))
    records = list(result.scalars().all())
    await provider.sync_zone(zone, records)

    zone.synced_at = datetime.now(UTC)
    await db.flush()
