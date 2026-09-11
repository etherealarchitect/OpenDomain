import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.domain import Domain, DomainEvent, DomainEventType, DomainStatus, DomainTransfer
from backend.app.models.user import User
from backend.app.schemas.domain import DomainRegister, DomainSearchResult, DomainTransferIn, DomainUpdate
from backend.app.services.epp.client import EppClient


TLD_PRICES_CENTS = {
    "com": 1099, "net": 1199, "org": 999, "io": 3999, "dev": 1299,
    "app": 1499, "co": 2999, "me": 899, "xyz": 199, "info": 299,
    "tech": 499, "online": 399, "site": 299, "store": 599, "cloud": 999,
}


class DomainService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.epp = EppClient()

    async def search(self, query: str, tlds: list[str] | None = None) -> list[DomainSearchResult]:
        if "." in query:
            name, tld = query.rsplit(".", 1)
            search_tlds = [tld]
        else:
            name = query
            search_tlds = tlds or ["com", "net", "org", "io", "dev", "app", "co"]

        results = []
        for tld in search_tlds:
            domain_name = f"{name}.{tld}"
            available = await self.epp.check_domain(domain_name)
            price = TLD_PRICES_CENTS.get(tld, 1499)
            results.append(DomainSearchResult(
                domain=domain_name,
                available=available,
                price_cents=price if available else None,
            ))
        return results

    async def register(self, data: DomainRegister, user: User) -> Domain:
        name, tld = data.domain.rsplit(".", 1)
        now = datetime.now(UTC)

        nameservers = ",".join(data.nameservers) if data.nameservers else "ns1.opendomain.local,ns2.opendomain.local"
        auth_code = secrets.token_urlsafe(16)

        domain = Domain(
            name=data.domain.lower(),
            tld=tld,
            status=DomainStatus.ACTIVE,
            owner_id=user.id,
            registrant_contact_id=data.registrant_contact_id,
            nameservers=nameservers,
            epp_auth_code=auth_code,
            auto_renew=data.auto_renew,
            privacy_enabled=data.privacy_enabled,
            registration_date=now,
            expiry_date=now + timedelta(days=365 * data.period_years),
            registration_period_years=data.period_years,
            price_cents=TLD_PRICES_CENTS.get(tld, 1499),
            renewal_price_cents=TLD_PRICES_CENTS.get(tld, 1499),
        )
        self.db.add(domain)
        await self.db.flush()

        await self.epp.create_domain(domain)

        event = DomainEvent(
            domain_id=domain.id,
            event_type=DomainEventType.REGISTERED,
            details=f"Registered for {data.period_years} year(s)",
            actor_id=user.id,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(domain)
        return domain

    async def list_for_user(
        self, user_id: uuid.UUID, status_filter: str | None, page: int, per_page: int
    ) -> list[Domain]:
        query = select(Domain).where(Domain.owner_id == user_id)
        if status_filter:
            query = query.where(Domain.status == status_filter)
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> Domain | None:
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, domain_id: uuid.UUID, data: DomainUpdate, user_id: uuid.UUID) -> Domain | None:
        domain = await self.get(domain_id, user_id)
        if not domain:
            return None

        updates = data.model_dump(exclude_unset=True)
        if "nameservers" in updates and updates["nameservers"]:
            updates["nameservers"] = ",".join(updates["nameservers"])

        for field, value in updates.items():
            setattr(domain, field, value)

        await self.db.flush()
        await self.db.refresh(domain)
        return domain

    async def renew(self, domain_id: uuid.UUID, years: int, user_id: uuid.UUID) -> Domain:
        domain = await self.get(domain_id, user_id)
        if not domain:
            raise ValueError("Domain not found")
        if domain.status not in (DomainStatus.ACTIVE, DomainStatus.EXPIRED):
            raise ValueError(f"Cannot renew domain in {domain.status} state")

        domain.expiry_date += timedelta(days=365 * years)
        domain.last_renewed = datetime.now(UTC)
        if domain.status == DomainStatus.EXPIRED:
            domain.status = DomainStatus.ACTIVE

        event = DomainEvent(
            domain_id=domain.id,
            event_type=DomainEventType.RENEWED,
            details=f"Renewed for {years} year(s)",
            actor_id=user_id,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(domain)
        return domain

    async def set_lock(self, domain_id: uuid.UUID, locked: bool, user_id: uuid.UUID) -> Domain:
        domain = await self.get(domain_id, user_id)
        if not domain:
            raise ValueError("Domain not found")
        domain.locked = locked
        event_type = DomainEventType.LOCKED if locked else DomainEventType.UNLOCKED
        event = DomainEvent(domain_id=domain.id, event_type=event_type, actor_id=user_id)
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(domain)
        return domain

    async def get_auth_code(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> str:
        domain = await self.get(domain_id, user_id)
        if not domain:
            raise ValueError("Domain not found")
        if domain.locked:
            raise ValueError("Domain must be unlocked to retrieve auth code")
        return domain.epp_auth_code or ""

    async def initiate_transfer_in(self, data: DomainTransferIn, user: User) -> DomainTransfer:
        name_parts = data.domain.lower().rsplit(".", 1)
        if len(name_parts) != 2:
            raise ValueError("Invalid domain name")
        tld = name_parts[1]
        now = datetime.now(UTC)

        domain = Domain(
            name=data.domain.lower(),
            tld=tld,
            status=DomainStatus.PENDING_TRANSFER,
            owner_id=user.id,
            registrant_contact_id=data.registrant_contact_id,
            nameservers="ns1.opendomain.local,ns2.opendomain.local",
            epp_auth_code=data.auth_code,
            auto_renew=True,
            privacy_enabled=True,
            registration_date=now,
            expiry_date=now + timedelta(days=365),
            registration_period_years=1,
            price_cents=TLD_PRICES_CENTS.get(tld, 1499),
            renewal_price_cents=TLD_PRICES_CENTS.get(tld, 1499),
        )
        self.db.add(domain)
        await self.db.flush()

        transfer = DomainTransfer(
            domain_id=domain.id,
            auth_code=data.auth_code,
            from_registrar="external",
            to_registrar="OpenDomain",
            initiated_by=user.id,
        )
        self.db.add(transfer)

        event = DomainEvent(
            domain_id=domain.id,
            event_type=DomainEventType.TRANSFERRED_IN,
            details=f"Transfer initiated from external registrar",
            actor_id=user.id,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(transfer)
        return transfer

    async def initiate_transfer_out(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        domain = await self.get(domain_id, user_id)
        if not domain:
            raise ValueError("Domain not found")
        if domain.status != DomainStatus.ACTIVE:
            raise ValueError("Only active domains can be transferred out")

        domain.locked = False
        domain.epp_auth_code = secrets.token_urlsafe(16)

        event = DomainEvent(
            domain_id=domain.id,
            event_type=DomainEventType.TRANSFERRED_OUT,
            details="Transfer out initiated, domain unlocked and auth code regenerated",
            actor_id=user_id,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(domain)
        return {"auth_code": domain.epp_auth_code, "domain": domain}

    async def delete(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> None:
        domain = await self.get(domain_id, user_id)
        if not domain:
            raise ValueError("Domain not found")
        domain.status = DomainStatus.PENDING_DELETE
        event = DomainEvent(
            domain_id=domain.id, event_type=DomainEventType.DELETED, actor_id=user_id
        )
        self.db.add(event)
