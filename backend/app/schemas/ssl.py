from datetime import datetime

from pydantic import BaseModel


class SslCertificateCreate(BaseModel):
    domain_id: str
    domain_names: list[str] | None = None
    auto_renew: bool = True


class SslCertificateResponse(BaseModel):
    id: str
    domain_id: str
    provider: str
    status: str
    domain_names: str
    issued_at: datetime | None
    expires_at: datetime | None
    auto_renew: bool
    created_at: datetime

    model_config = {"from_attributes": True}
