import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.dns import DnsZone


class DnssecService:
    def __init__(self, db: AsyncSession):
        self.db = db

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
        zone.dnssec_enabled = True
        zone.dnssec_algorithm = algorithm
        key_tag = secrets.randbelow(65536)
        zone.dnssec_ds_record = f"{key_tag} 13 2 {secrets.token_hex(32).upper()}"
        await self.db.flush()
        return {
            "enabled": True,
            "algorithm": algorithm,
            "ds_record": zone.dnssec_ds_record,
        }

    async def disable_dnssec(self, domain_id: uuid.UUID, user_id: uuid.UUID):
        zone = await self._get_zone(domain_id, user_id)
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
        key_tag = secrets.randbelow(65536)
        zone.dnssec_ds_record = f"{key_tag} 13 2 {secrets.token_hex(32).upper()}"
        await self.db.flush()
        return {
            "rotated": True,
            "algorithm": algorithm,
            "new_ds_record": zone.dnssec_ds_record,
        }
