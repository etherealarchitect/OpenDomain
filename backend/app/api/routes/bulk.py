from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.bulk import (
    BulkDnsUpdate,
    BulkDomainRegister,
    BulkActionResponse,
    BulkRenew,
)
from backend.app.services.bulk_service import BulkService

router = APIRouter(prefix="/bulk", tags=["bulk"])


class BulkDomainIds(BaseModel):
    domain_ids: list[str]


@router.post("/register", response_model=BulkActionResponse, status_code=status.HTTP_201_CREATED)
async def bulk_register(data: BulkDomainRegister, db: DbSession, current_user: CurrentUser):
    service = BulkService(db)
    return await service.bulk_register(data, current_user)


@router.post("/renew", response_model=BulkActionResponse)
async def bulk_renew(data: BulkRenew, db: DbSession, current_user: CurrentUser):
    service = BulkService(db)
    return await service.bulk_renew(data, current_user.id)


@router.post("/dns", response_model=BulkActionResponse)
async def bulk_dns_update(data: BulkDnsUpdate, db: DbSession, current_user: CurrentUser):
    service = BulkService(db)
    return await service.bulk_dns_update(data, current_user.id)


@router.post("/lock", response_model=BulkActionResponse)
async def bulk_lock(data: BulkDomainIds, db: DbSession, current_user: CurrentUser):
    service = BulkService(db)
    return await service.bulk_set_lock(data.domain_ids, True, current_user.id)


@router.post("/unlock", response_model=BulkActionResponse)
async def bulk_unlock(data: BulkDomainIds, db: DbSession, current_user: CurrentUser):
    service = BulkService(db)
    return await service.bulk_set_lock(data.domain_ids, False, current_user.id)
