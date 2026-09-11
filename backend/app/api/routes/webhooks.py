import uuid

from fastapi import APIRouter, Query, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.webhook import (
    WebhookCreate,
    WebhookDeliveryResponse,
    WebhookResponse,
)
from backend.app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(data: WebhookCreate, db: DbSession, current_user: CurrentUser):
    service = WebhookService(db)
    return await service.create_webhook(data, current_user.id)


@router.get("/", response_model=list[WebhookResponse])
async def list_webhooks(db: DbSession, current_user: CurrentUser):
    service = WebhookService(db)
    return await service.list_webhooks(current_user.id)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(webhook_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = WebhookService(db)
    await service.delete_webhook(webhook_id, current_user.id)


@router.get("/{webhook_id}/deliveries", response_model=list[WebhookDeliveryResponse])
async def list_deliveries(
    webhook_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=200),
):
    service = WebhookService(db)
    return await service.list_deliveries(webhook_id, current_user.id, limit)
