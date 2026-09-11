import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: str | None = None
    phone: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    company: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    company: str | None
    phone: str | None
    role: str
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
