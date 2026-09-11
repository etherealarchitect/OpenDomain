from datetime import datetime

from pydantic import BaseModel


class WebhookCreate(BaseModel):
    url: str
    events: list[str]
    secret: str | None = None


class WebhookUpdate(BaseModel):
    url: str | None = None
    events: list[str] | None = None
    active: bool | None = None


class WebhookResponse(BaseModel):
    id: str
    url: str
    events: str
    active: bool
    last_triggered: datetime | None
    failure_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookDeliveryResponse(BaseModel):
    id: str
    webhook_id: str
    event_type: str
    payload: str
    response_status: int | None
    success: bool
    attempted_at: datetime

    model_config = {"from_attributes": True}
