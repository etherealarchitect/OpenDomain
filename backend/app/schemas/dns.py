import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class DnsRecordCreate(BaseModel):
    record_type: str
    name: str
    content: str
    ttl: int = 3600
    priority: int | None = None
    proxied: bool = False
    comment: str | None = None

    @field_validator("record_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {"A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA", "PTR", "ALIAS", "TLSA", "DS"}
        if v.upper() not in valid:
            raise ValueError(f"Invalid record type. Must be one of: {', '.join(sorted(valid))}")
        return v.upper()

    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        if v < 60 or v > 86400:
            raise ValueError("TTL must be between 60 and 86400 seconds")
        return v


class DnsRecordUpdate(BaseModel):
    content: str | None = None
    ttl: int | None = None
    priority: int | None = None
    proxied: bool | None = None
    enabled: bool | None = None
    comment: str | None = None


class DnsRecordResponse(BaseModel):
    id: uuid.UUID
    zone_id: uuid.UUID
    record_type: str
    name: str
    content: str
    ttl: int
    priority: int | None
    proxied: bool
    enabled: bool
    comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DnsZoneResponse(BaseModel):
    id: uuid.UUID
    domain_id: uuid.UUID
    zone_name: str
    primary_ns: str
    serial: int
    default_ttl: int
    dnssec_enabled: bool
    records: list[DnsRecordResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DnsZoneExport(BaseModel):
    zone_name: str
    zone_file: str


class BulkDnsRecordCreate(BaseModel):
    records: list[DnsRecordCreate]


class DnsTemplateApply(BaseModel):
    template: str
    params: dict[str, str] = {}
