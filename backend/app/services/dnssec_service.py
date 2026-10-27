import logging
import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.dns import DnsZone
from backend.app.services.dns import get_dns_provider, publish_zone

logger = logging.getLogger(__name__)


class DnssecService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _simulated_ds_record(algorithm: str) -> str:
        """Stand-in DS record used when no authoritative provider is configured."""
        return f"{secrets.randbelow(65536)} 13 2 {secrets.token_hex(32).upper()}"

    async def _get_zone(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> DnsZone:
        from backend.app.models.domain import Domain
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        )
        domain = result.scalar_one_or_none()
        if not domain:
            raise ValueError("Domain not found")
        result = await self.db.execute(
            select(DnsZone).where(DnsZone.domain_id == domain_id)
        )
        zone = result.scalar_one_or_none()
        if not zone:
            raise ValueError("DNS zone not found")
        return zone

    async def enable_dnssec(
        self, domain_id: uuid.UUID, user_id: uuid.UUID, algorithm: str = "ECDSAP256SHA256"
    ) -> dict:
        zone = await self._get_zone(domain_id, user_id)
        provider = get_dns_provider()
        ds_record: str | None = None
        if provider is not None:
            # Publishing first guarantees the zone exists before it is signed.
            await publish_zone(self.db, zone)
            ds_record = await provider.set_dnssec(zone.zone_name, True)
        else:
            ds_record = self._simulated_ds_record(algorithm)

        zone.dnssec_enabled = True
        zone.dnssec_algorithm = algorithm
        zone.dnssec_ds_record = ds_record
        await self.db.flush()
        return {
            "enabled": True,
            "algorithm": algorithm,
            "ds_record": zone.dnssec_ds_record,
        }

    async def get_status(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        zone = await self._get_zone(domain_id, user_id)
        return {
            "zone_name": zone.zone_name,
            "dnssec_enabled": zone.dnssec_enabled,
            "algorithm": zone.dnssec_algorithm,
            "ds_record": zone.dnssec_ds_record,
        }

    async def disable_dnssec(self, domain_id: uuid.UUID, user_id: uuid.UUID):
        zone = await self._get_zone(domain_id, user_id)
        provider = get_dns_provider()
        if provider is not None and await provider.get_zone(zone.zone_name) is not None:
            await provider.set_dnssec(zone.zone_name, False)
        zone.dnssec_enabled = False
        zone.dnssec_algorithm = None
        zone.dnssec_ds_record = None
        await self.db.flush()

    async def get_ds_record(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> str | None:
        zone = await self._get_zone(domain_id, user_id)
        return zone.dnssec_ds_record

    async def rotate_keys(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        zone = await self._get_zone(domain_id, user_id)
        if not zone.dnssec_enabled:
            raise ValueError("DNSSEC is not enabled for this domain")
        algorithm = zone.dnssec_algorithm or "ECDSAP256SHA256"
        provider = get_dns_provider()
        if provider is not None:
            zone.dnssec_ds_record = await provider.rotate_dnssec_key(zone.zone_name)
        else:
            zone.dnssec_ds_record = self._simulated_ds_record(algorithm)
        await self.db.flush()
        return {
            "rotated": True,
            "algorithm": algorithm,
            "new_ds_record": zone.dnssec_ds_record,
        }
