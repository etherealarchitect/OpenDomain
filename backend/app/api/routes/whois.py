from datetime import UTC, datetime

from backend.app.api.routes.auth import client_ip, enforce_auth_rate_limit
from backend.app.services.whois_service import WhoisService
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/whois", tags=["whois"])
whois_service = WhoisService()


class WhoisLookupRequest(BaseModel):
    domain_name: str = Field(min_length=3, max_length=253)


class WhoisLookupResponse(BaseModel):
    domain_name: str
    lookup_status: str
    source: str
    registrar: str | None
    creation_date: datetime | None
    expiration_date: datetime | None
    updated_date: datetime | None
    nameservers: list[str]
    status: list[str]
    dnssec: bool | None
    warnings: list[str]
    looked_up_at: datetime


@router.post("/", response_model=WhoisLookupResponse, summary="Look up public domain registration data")
async def whois_lookup(data: WhoisLookupRequest, request: Request):
    """Look up a normalized domain through RDAP with a bounded WHOIS fallback."""
    await enforce_auth_rate_limit("whois-ip", client_ip(request), 60, 60 * 60)
    try:
        result = await whois_service.lookup(data.domain_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return WhoisLookupResponse(
        domain_name=result.domain_name,
        lookup_status=result.lookup_status,
        source=result.source,
        registrar=result.registrar,
        creation_date=result.creation_date,
        expiration_date=result.expiration_date,
        updated_date=result.updated_date,
        nameservers=result.nameservers,
        status=result.status,
        dnssec=result.dnssec,
        warnings=result.warnings,
        looked_up_at=datetime.now(UTC),
    )
