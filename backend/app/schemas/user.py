import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    full_name: str = Field(min_length=2, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().casefold()

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        if not any(char.islower() for char in value):
            raise ValueError("Password must include a lowercase letter")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must include an uppercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must include a number")
        return value


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)


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
    onboarding_state: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().casefold()


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=12, max_length=72)

    @field_validator("current_password")
    @classmethod
    def validate_current_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return UserCreate.validate_password(value)


class RegisterResponse(BaseModel):
    message: str
    email: str
    verification_required: bool = True


class GenericAuthResponse(BaseModel):
    message: str


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32, max_length=512)


class MfaChallengeResponse(BaseModel):
    challenge_id: uuid.UUID
    next_step: str
    expires_in_seconds: int


class MfaEnrollmentResponse(MfaChallengeResponse):
    qr_data_uri: str
    secret: str


class MfaChallengeRequest(BaseModel):
    challenge_id: uuid.UUID


class MfaVerifyRequest(MfaChallengeRequest):
    code: str = Field(min_length=6, max_length=16)


class MfaSetupResponse(BaseModel):
    backup_codes: list[str]
    message: str


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().casefold()


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=32, max_length=512)
    new_password: str = Field(min_length=12, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return UserCreate.validate_password(value)


class SessionResponse(BaseModel):
    authenticated: bool = True
    user: UserResponse
