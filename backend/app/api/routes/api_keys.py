import uuid

from fastapi import APIRouter, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyCreated,
    ApiKeyResponse,
)
from backend.app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("/", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(data: ApiKeyCreate, db: DbSession, current_user: CurrentUser):
    service = ApiKeyService(db)
    return await service.create_key(data, current_user.id)


@router.get("/", response_model=list[ApiKeyResponse])
async def list_api_keys(db: DbSession, current_user: CurrentUser):
    service = ApiKeyService(db)
    return await service.list_keys(current_user.id)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(key_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = ApiKeyService(db)
    await service.revoke_key(key_id, current_user.id)
