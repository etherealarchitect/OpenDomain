from pydantic import BaseModel


class BulkDomainItem(BaseModel):
    domain: str
    period_years: int = 1
    contact_id: str


class BulkDomainRegister(BaseModel):
    domains: list[BulkDomainItem]


class BulkDnsRecord(BaseModel):
    record_type: str
    name: str
    content: str
    ttl: int = 3600
    priority: int | None = None


class BulkDnsUpdate(BaseModel):
    domain_ids: list[str]
    records: list[BulkDnsRecord]


class BulkRenew(BaseModel):
    domain_ids: list[str]
    years: int = 1


class BulkLock(BaseModel):
    domain_ids: list[str]
    lock: bool = True


class BulkActionResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: list[dict]
