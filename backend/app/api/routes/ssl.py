import uuid

from fastapi import APIRouter, HTTPException, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.ssl import (
    SslCertificateCreate,
    SslCertificateResponse,
)
from backend.app.services.ssl_service import SslService

router = APIRouter(prefix="/ssl", tags=["ssl"])


@router.post("/certificates", response_model=SslCertificateResponse, status_code=status.HTTP_201_CREATED)
async def request_certificate(data: SslCertificateCreate, db: DbSession, current_user: CurrentUser):
    service = SslService(db)
    return await service.request_certificate(data, current_user.id)


@router.get("/certificates", response_model=list[SslCertificateResponse])
async def list_certificates(db: DbSession, current_user: CurrentUser):
    service = SslService(db)
    return await service.list_certificates(current_user.id)


@router.get("/certificates/{cert_id}", response_model=SslCertificateResponse)
async def get_certificate(cert_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = SslService(db)
    cert = await service.get_certificate(cert_id, current_user.id)
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    return cert


@router.post("/certificates/{cert_id}/revoke")
async def revoke_certificate(cert_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = SslService(db)
    await service.revoke_certificate(cert_id, current_user.id)
    return {"revoked": True}


@router.post("/certificates/{cert_id}/renew", response_model=SslCertificateResponse)
async def renew_certificate(cert_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = SslService(db)
    return await service.renew_certificate(cert_id, current_user.id)
