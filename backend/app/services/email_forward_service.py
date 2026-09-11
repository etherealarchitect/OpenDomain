import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.domain import Domain
from backend.app.models.email_forward import EmailForward


class EmailForwardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_forward(self, user_id: uuid.UUID, data) -> EmailForward:
        domain_id = uuid.UUID(data.domain_id)
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Domain not found or you don't own it")

        forward = EmailForward(
            domain_id=domain_id,
            user_id=user_id,
            source_address=data.source_address,
            destination_email=data.destination_email,
        )
        self.db.add(forward)
        await self.db.flush()
        await self.db.refresh(forward)
        return forward

    async def list_forwards(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> list[EmailForward]:
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Domain not found")
        result = await self.db.execute(
            select(EmailForward)
            .where(EmailForward.domain_id == domain_id)
            .order_by(EmailForward.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_forward(self, forward_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(EmailForward).where(EmailForward.id == forward_id, EmailForward.user_id == user_id)
        )
        forward = result.scalar_one_or_none()
        if not forward:
            raise ValueError("Forward not found")
        await self.db.delete(forward)

    async def toggle_forward(self, forward_id: uuid.UUID, user_id: uuid.UUID) -> EmailForward:
        result = await self.db.execute(
            select(EmailForward).where(EmailForward.id == forward_id, EmailForward.user_id == user_id)
        )
        forward = result.scalar_one_or_none()
        if not forward:
            raise ValueError("Forward not found")
        forward.active = not forward.active
        await self.db.flush()
        await self.db.refresh(forward)
        return forward
