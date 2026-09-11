import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    label: str
    first_name: str
    last_name: str
    organization: str | None = None
    email: EmailStr
    phone: str
    fax: str | None = None
    address_line1: str
    address_line2: str | None = None
    city: str
    state_province: str | None = None
    postal_code: str
    country_code: str


class ContactUpdate(BaseModel):
    label: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    organization: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address_line1: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country_code: str | None = None


class ContactResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    label: str
    first_name: str
    last_name: str
    organization: str | None
    email: str
    phone: str
    city: str
    country_code: str
    created_at: datetime

    model_config = {"from_attributes": True}
