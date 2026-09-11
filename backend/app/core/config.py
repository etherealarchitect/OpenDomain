import base64
import hashlib

from cryptography.fernet import Fernet
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OpenDomain"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    debug: bool = False
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://opendomain:opendomain@localhost:5432/opendomain"
    redis_url: str = "redis://localhost:6379/0"

    # Required outside local development. SECRET_KEY also provides the default
    # derivation source for the independent encryption and token-pepper keys.
    secret_key: str = "change-me-to-a-random-secret-key"
    token_pepper: str | None = None
    auth_encryption_key: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    session_expire_days: int = Field(default=14, ge=1, le=90)
    auth_challenge_expire_minutes: int = Field(default=10, ge=1, le=30)
    auth_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    cookie_secure: bool = False
    cookie_domain: str | None = None

    resend_api_key: str | None = None
    mail_from: str = "OpenDomain <onboarding@resend.dev>"

    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("secret_key")
    @classmethod
    def require_safe_production_secret(cls, value: str) -> str:
        if value == "change-me-to-a-random-secret-key":
            return value
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return value

    @property
    def effective_token_pepper(self) -> str:
        return self.token_pepper or hashlib.sha256(f"{self.secret_key}:token".encode()).hexdigest()

    @property
    def effective_auth_encryption_key(self) -> str:
        if self.auth_encryption_key:
            return self.auth_encryption_key
        return base64.urlsafe_b64encode(
            hashlib.sha256(f"{self.secret_key}:encryption".encode()).digest()
        ).decode()

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    def validate_production(self) -> None:
        if self.auth_encryption_key:
            try:
                Fernet(self.auth_encryption_key.encode())
            except (TypeError, ValueError) as exc:
                raise RuntimeError("AUTH_ENCRYPTION_KEY must be a valid Fernet key") from exc
        if not self.is_production:
            return
        if self.secret_key == "change-me-to-a-random-secret-key" or len(self.secret_key) < 32:
            raise RuntimeError("A strong SECRET_KEY is required in production")
        if not self.auth_encryption_key:
            raise RuntimeError("AUTH_ENCRYPTION_KEY is required in production")
        try:
            Fernet(self.auth_encryption_key.encode())
        except (TypeError, ValueError) as exc:
            raise RuntimeError("AUTH_ENCRYPTION_KEY must be a valid Fernet key") from exc
        if not self.cookie_secure:
            raise RuntimeError("COOKIE_SECURE must be true in production")
        if not self.resend_api_key:
            raise RuntimeError("RESEND_API_KEY is required in production")
        if self.mail_from.endswith("@resend.dev>"):
            raise RuntimeError("MAIL_FROM must use a verified production sender")

    anthropic_model: str = "anthropic.claude-fable-5"
    aws_region: str = "ap-southeast-2"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    epp_host: str = "epp.registry.example"
    epp_port: int = 700
    epp_client_id: str = ""
    epp_password: str = ""
    epp_cert_path: str = "./certs/epp-client.pem"
    epp_key_path: str = "./certs/epp-client-key.pem"
    epp_simulate: bool = True

    dns_provider: str = "powerdns"
    powerdns_api_url: str = "http://localhost:8081"
    powerdns_api_key: str = "change-me"

    whois_privacy_default: bool = True

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
