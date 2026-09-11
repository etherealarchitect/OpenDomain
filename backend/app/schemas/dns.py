import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DnsRecordCreate(BaseModel):
    record_type: str
    name: str = Field(min_length=1, max_length=253)
    content: str = Field(min_length=1, max_length=4096)
    ttl: int = 3600
    priority: int | None = Field(default=None, ge=0, le=65535)
    proxied: bool = False
    comment: str | None = None

    @field_validator("record_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {
            "A",
            "AAAA",
            "CNAME",
            "MX",
            "TXT",
            "NS",
            "SRV",
            "CAA",
            "PTR",
            "ALIAS",
            "TLSA",
            "DS",
        }
        if v.upper() not in valid:
            raise ValueError(f"Invalid record type. Must be one of: {', '.join(sorted(valid))}")
        return v.upper()

    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        if v < 0 or v > 2147483647:
            raise ValueError("TTL must be between 0 and 2147483647 seconds")
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


class DnsDiscoveryRecord(BaseModel):
    record_type: str
    name: str
    content: str
    ttl: int
    priority: int | None = None
    warnings: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DnsDiscoveryResponse(BaseModel):
    domain_name: str
    records: list[DnsDiscoveryRecord]
    queried_types: list[str]
    warnings: list[str] = []


class DnsImportPreviewRequest(BaseModel):
    records: list[DnsRecordCreate] = Field(min_length=1, max_length=500)


class DnsImportPreviewResponse(BaseModel):
    additions: list[DnsRecordCreate]
    unchanged: list[DnsRecordCreate]
    conflicts: list[DnsRecordCreate]
    normalized_records: list[DnsRecordCreate]
    revision: str
    warnings: list[str] = Field(default_factory=list)


class DnsImportApplyRequest(DnsImportPreviewRequest):
    mode: str
    expected_revision: str = Field(pattern=r"^[a-f0-9]{64}$")
    confirm_replace: bool = False

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        if value not in {"merge", "replace"}:
            raise ValueError("mode must be either 'merge' or 'replace'")
        return value


class DnsTemplateApply(BaseModel):
    template: str
    params: dict[str, str] = {}
