import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.schemas.dns import DnsRecordCreate
from backend.app.schemas.domain import DomainRegister
from backend.app.services.dns_service import DnsService
from backend.app.services.domain_service import DomainService


class BulkService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.domain_service = DomainService(db)
        self.dns_service = DnsService(db)

    async def bulk_register(self, user: User, data) -> dict:
        results = []
        succeeded = 0
        failed = 0
        for item in data.domains:
            try:
                reg_data = DomainRegister(
                    domain=item.domain,
                    period_years=item.period_years,
                    registrant_contact_id=uuid.UUID(item.contact_id),
                )
                domain = await self.domain_service.register(reg_data, user)
                results.append({"domain": item.domain, "status": "registered", "id": str(domain.id)})
                succeeded += 1
            except Exception as e:
                results.append({"domain": item.domain, "status": "failed", "error": str(e)})
                failed += 1
        return {"total": len(data.domains), "succeeded": succeeded, "failed": failed, "results": results}

    async def bulk_renew(self, user_id: uuid.UUID, data) -> dict:
        results = []
        succeeded = 0
        failed = 0
        for domain_id_str in data.domain_ids:
            try:
                domain = await self.domain_service.renew(uuid.UUID(domain_id_str), data.years, user_id)
                results.append({"domain_id": domain_id_str, "status": "renewed", "new_expiry": str(domain.expiry_date)})
                succeeded += 1
            except Exception as e:
                results.append({"domain_id": domain_id_str, "status": "failed", "error": str(e)})
                failed += 1
        return {"total": len(data.domain_ids), "succeeded": succeeded, "failed": failed, "results": results}

    async def bulk_dns_update(self, user_id: uuid.UUID, data) -> dict:
        results = []
        succeeded = 0
        failed = 0
        for domain_id_str in data.domain_ids:
            domain_id = uuid.UUID(domain_id_str)
            domain_results = []
            domain_ok = True
            for rec in data.records:
                try:
                    record_data = DnsRecordCreate(
                        record_type=rec.record_type,
                        name=rec.name,
                        content=rec.content,
                        ttl=rec.ttl,
                        priority=rec.priority,
                    )
                    await self.dns_service.create_record(domain_id, record_data, user_id)
                    domain_results.append({"record": f"{rec.record_type} {rec.name}", "status": "created"})
                except Exception as e:
                    domain_results.append({"record": f"{rec.record_type} {rec.name}", "status": "failed", "error": str(e)})
                    domain_ok = False
            if domain_ok:
                succeeded += 1
            else:
                failed += 1
            results.append({"domain_id": domain_id_str, "records": domain_results})
        return {"total": len(data.domain_ids), "succeeded": succeeded, "failed": failed, "results": results}

    async def bulk_lock(self, user_id: uuid.UUID, domain_ids: list[str], lock: bool = True) -> dict:
        results = []
        succeeded = 0
        failed = 0
        for domain_id_str in domain_ids:
            try:
                await self.domain_service.set_lock(uuid.UUID(domain_id_str), lock, user_id)
                results.append({"domain_id": domain_id_str, "status": "locked" if lock else "unlocked"})
                succeeded += 1
            except Exception as e:
                results.append({"domain_id": domain_id_str, "status": "failed", "error": str(e)})
                failed += 1
        return {"total": len(domain_ids), "succeeded": succeeded, "failed": failed, "results": results}
