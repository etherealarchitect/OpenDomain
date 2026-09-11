import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.domain import Domain
from backend.app.models.ssl_certificate import CertificateStatus, SslCertificate


class SslService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def request_certificate(self, user_id: uuid.UUID, data) -> SslCertificate:
        domain_id = uuid.UUID(data.domain_id)
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        )
        domain = result.scalar_one_or_none()
        if not domain:
            raise ValueError("Domain not found or you don't own it")

        domain_names = data.domain_names if data.domain_names else [domain.name]

        cert = SslCertificate(
            domain_id=domain_id,
            user_id=user_id,
            domain_names=",".join(domain_names),
            auto_renew=data.auto_renew,
            status=CertificateStatus.PENDING,
        )
        self.db.add(cert)
        await self.db.flush()
        await self.db.refresh(cert)
        return cert

    async def list_certificates(self, user_id: uuid.UUID) -> list[SslCertificate]:
        result = await self.db.execute(
            select(SslCertificate)
            .where(SslCertificate.user_id == user_id)
            .order_by(SslCertificate.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_certificate(self, cert_id: uuid.UUID, user_id: uuid.UUID) -> SslCertificate | None:
        result = await self.db.execute(
            select(SslCertificate).where(SslCertificate.id == cert_id, SslCertificate.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def revoke_certificate(self, cert_id: uuid.UUID, user_id: uuid.UUID):
        cert = await self.get_certificate(cert_id, user_id)
        if not cert:
            raise ValueError("Certificate not found")
        cert.status = CertificateStatus.REVOKED
        await self.db.flush()

    async def renew_certificate(self, cert_id: uuid.UUID, user_id: uuid.UUID) -> SslCertificate:
        cert = await self.get_certificate(cert_id, user_id)
        if not cert:
            raise ValueError("Certificate not found")
        cert.last_renewal_attempt = datetime.now(UTC)
        cert.status = CertificateStatus.PENDING
        await self.db.flush()
        await self.db.refresh(cert)
        return cert
