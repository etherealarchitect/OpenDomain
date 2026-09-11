from datetime import datetime

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    name: str
    scopes: list[str] | None = None
    expires_in_days: int | None = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    scopes: str | None
    last_used: datetime | None
    expires_at: datetime | None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreated(BaseModel):
    id: str
    name: str
    key: str
    prefix: str
    scopes: str | None
    expires_at: datetime | None
    created_at: datetime
