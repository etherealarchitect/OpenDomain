import json
import logging
import secrets
import uuid
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.webhook import Webhook, WebhookDelivery, WebhookEventType

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_webhook(self, user_id: uuid.UUID, data) -> Webhook:
        webhook = Webhook(
            user_id=user_id,
            url=data.url,
            secret=data.secret or secrets.token_hex(32),
            events=",".join(data.events),
        )
        self.db.add(webhook)
        await self.db.flush()
        await self.db.refresh(webhook)
        return webhook

    async def list_webhooks(self, user_id: uuid.UUID) -> list[Webhook]:
        result = await self.db.execute(
            select(Webhook).where(Webhook.user_id == user_id).order_by(Webhook.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_webhook(self, webhook_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == user_id)
        )
        webhook = result.scalar_one_or_none()
        if not webhook:
            raise ValueError("Webhook not found")
        await self.db.delete(webhook)

    async def update_webhook(self, webhook_id: uuid.UUID, user_id: uuid.UUID, data):
        result = await self.db.execute(
            select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == user_id)
        )
        webhook = result.scalar_one_or_none()
        if not webhook:
            raise ValueError("Webhook not found")
        if data.url is not None:
            webhook.url = data.url
        if data.events is not None:
            webhook.events = ",".join(data.events)
        if data.active is not None:
            webhook.active = data.active
        await self.db.flush()
        await self.db.refresh(webhook)
        return webhook

    async def fire_event(self, user_id: uuid.UUID, event_type: str, payload: dict):
        result = await self.db.execute(
            select(Webhook).where(Webhook.user_id == user_id, Webhook.active.is_(True))
        )
        webhooks = result.scalars().all()
        payload_str = json.dumps(payload)

        async with httpx.AsyncClient(timeout=10) as client:
            for webhook in webhooks:
                subscribed = webhook.events.split(",")
                if event_type not in subscribed:
                    continue

                delivery = WebhookDelivery(
                    webhook_id=webhook.id,
                    event_type=WebhookEventType(event_type),
                    payload=payload_str,
                    attempted_at=datetime.now(UTC),
                )

                try:
                    start = datetime.now(UTC)
                    resp = await client.post(
                        webhook.url,
                        content=payload_str,
                        headers={
                            "Content-Type": "application/json",
                            "X-Webhook-Secret": webhook.secret,
                            "X-Event-Type": event_type,
                        },
                    )
                    elapsed_ms = int((datetime.now(UTC) - start).total_seconds() * 1000)
                    delivery.response_status = resp.status_code
                    delivery.response_body = resp.text[:2000]
                    delivery.success = 200 <= resp.status_code < 300
                    delivery.duration_ms = elapsed_ms
                    webhook.last_triggered = datetime.now(UTC)
                    if not delivery.success:
                        webhook.failure_count += 1
                except Exception as e:
                    logger.warning("Webhook delivery failed for %s: %s", webhook.url, e)
                    delivery.success = False
                    delivery.response_body = str(e)[:2000]
                    webhook.failure_count += 1

                self.db.add(delivery)

        await self.db.flush()

    async def list_deliveries(self, webhook_id: uuid.UUID, user_id: uuid.UUID, limit: int = 50):
        result = await self.db.execute(
            select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == user_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Webhook not found")

        result = await self.db.execute(
            select(WebhookDelivery)
            .where(WebhookDelivery.webhook_id == webhook_id)
            .order_by(WebhookDelivery.attempted_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
