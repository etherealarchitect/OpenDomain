from datetime import datetime

from pydantic import BaseModel


class DomainWatchCreate(BaseModel):
    query: str
    notify_email: str | None = None


class DomainWatchResponse(BaseModel):
    id: str
    domain_name: str
    is_available: bool
    last_checked: datetime | None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UptimeCheckCreate(BaseModel):
    domain_id: str
    url: str
    check_interval_seconds: int = 300


class UptimeCheckResponse(BaseModel):
    id: str
    domain_id: str
    url: str
    status: str
    last_checked: datetime | None
    response_time_ms: int | None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SslMonitorResponse(BaseModel):
    id: str
    domain_id: str
    issuer: str | None
    valid_from: datetime | None
    valid_until: datetime | None
    last_checked: datetime | None
    auto_renew: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertRuleCreate(BaseModel):
    domain_id: str | None = None
    alert_type: str
    threshold_days: int | None = None
    webhook_url: str | None = None
    email: str | None = None


class AlertRuleResponse(BaseModel):
    id: str
    user_id: str
    domain_id: str | None
    alert_type: str
    threshold_days: int | None
    webhook_url: str | None
    email: str | None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id: str
    alert_type: str
    status: str
    title: str
    message: str
    domain_id: str | None
    created_at: datetime
    acknowledged_at: datetime | None

    model_config = {"from_attributes": True}
