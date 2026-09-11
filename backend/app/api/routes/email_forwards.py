import uuid

from fastapi import APIRouter, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.email_forward import (
    EmailForwardCreate,
    EmailForwardResponse,
)
from backend.app.services.email_forward_service import EmailForwardService

router = APIRouter(prefix="/domains/{domain_id}/email", tags=["email"])


@router.post("/", response_model=EmailForwardResponse, status_code=status.HTTP_201_CREATED)
async def create_forward(
    domain_id: uuid.UUID, data: EmailForwardCreate, db: DbSession, current_user: CurrentUser
):
    service = EmailForwardService(db)
    return await service.create_forward(domain_id, data, current_user.id)


@router.get("/", response_model=list[EmailForwardResponse])
async def list_forwards(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = EmailForwardService(db)
    return await service.list_forwards(domain_id, current_user.id)


@router.delete("/{forward_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forward(
    domain_id: uuid.UUID, forward_id: uuid.UUID, db: DbSession, current_user: CurrentUser
):
    service = EmailForwardService(db)
    await service.delete_forward(domain_id, forward_id, current_user.id)


@router.post("/{forward_id}/toggle", response_model=EmailForwardResponse)
async def toggle_forward(
    domain_id: uuid.UUID, forward_id: uuid.UUID, db: DbSession, current_user: CurrentUser
):
    service = EmailForwardService(db)
    return await service.toggle_forward(domain_id, forward_id, current_user.id)
