import uuid

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.domain import (
    DomainRegister,
    DomainRenew,
    DomainResponse,
    DomainSearch,
    DomainSearchResult,
    DomainTransferIn,
    DomainTransferResponse,
    DomainUpdate,
)
from backend.app.services.domain_service import DomainService

router = APIRouter(prefix="/domains", tags=["domains"])


@router.post("/search", response_model=list[DomainSearchResult])
async def search_domains(data: DomainSearch, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    return await service.search(data.query, data.tlds)


@router.post("/register", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def register_domain(data: DomainRegister, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    domain = await service.register(data, current_user)
    return domain


@router.get("/", response_model=list[DomainResponse])
async def list_domains(
    db: DbSession,
    current_user: CurrentUser,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
):
    service = DomainService(db)
    return await service.list_for_user(current_user.id, status_filter, page, per_page)


@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    domain = await service.get(domain_id, current_user.id)
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return domain


@router.patch("/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: uuid.UUID, data: DomainUpdate, db: DbSession, current_user: CurrentUser
):
    service = DomainService(db)
    domain = await service.update(domain_id, data, current_user.id)
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return domain


@router.post("/{domain_id}/renew", response_model=DomainResponse)
async def renew_domain(
    domain_id: uuid.UUID, data: DomainRenew, db: DbSession, current_user: CurrentUser
):
    service = DomainService(db)
    return await service.renew(domain_id, data.period_years, current_user.id)


@router.post("/{domain_id}/lock", response_model=DomainResponse)
async def lock_domain(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    return await service.set_lock(domain_id, True, current_user.id)


@router.post("/{domain_id}/unlock", response_model=DomainResponse)
async def unlock_domain(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    return await service.set_lock(domain_id, False, current_user.id)


@router.get("/{domain_id}/auth-code")
async def get_auth_code(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    code = await service.get_auth_code(domain_id, current_user.id)
    return {"auth_code": code}


@router.post("/transfer", response_model=DomainTransferResponse, status_code=status.HTTP_201_CREATED)
async def transfer_domain_in(data: DomainTransferIn, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    return await service.initiate_transfer_in(data, current_user)


@router.post("/{domain_id}/transfer-out")
async def transfer_domain_out(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    try:
        result = await service.initiate_transfer_out(domain_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"auth_code": result["auth_code"]}


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DomainService(db)
    await service.delete(domain_id, current_user.id)
