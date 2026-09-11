import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class DomainSearch(BaseModel):
    query: str
    tlds: list[str] | None = None

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip().lower()
        if not v or len(v) > 253:
            raise ValueError("Domain query must be 1-253 characters")
        return v


class DomainSearchResult(BaseModel):
    domain: str
    available: bool
    price_cents: int | None = None
    premium: bool = False


class DomainRegister(BaseModel):
    domain: str
    period_years: int = 1
    registrant_contact_id: uuid.UUID
    nameservers: list[str] | None = None
    privacy_enabled: bool = True
    auto_renew: bool = True


class DomainRenew(BaseModel):
    period_years: int = 1


class DomainTransferIn(BaseModel):
    domain: str
    auth_code: str
    registrant_contact_id: uuid.UUID


class DomainUpdate(BaseModel):
    nameservers: list[str] | None = None
    auto_renew: bool | None = None
    privacy_enabled: bool | None = None
    locked: bool | None = None
    registrant_contact_id: uuid.UUID | None = None
    admin_contact_id: uuid.UUID | None = None
    tech_contact_id: uuid.UUID | None = None
    billing_contact_id: uuid.UUID | None = None


class DomainResponse(BaseModel):
    id: uuid.UUID
    name: str
    tld: str
    status: str
    owner_id: uuid.UUID
    auto_renew: bool
    privacy_enabled: bool
    locked: bool
    nameservers: str | None
    registration_date: datetime
    expiry_date: datetime
    last_renewed: datetime | None
    price_cents: int
    renewal_price_cents: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DomainEventResponse(BaseModel):
    id: uuid.UUID
    domain_id: uuid.UUID
    event_type: str
    details: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DomainTransferResponse(BaseModel):
    id: uuid.UUID
    domain_id: uuid.UUID
    from_registrar: str | None
    to_registrar: str | None
    status: str
    initiated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
