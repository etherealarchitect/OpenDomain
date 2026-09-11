from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.whois_service import WhoisService

router = APIRouter(prefix="/whois", tags=["whois"])


class WhoisLookupRequest(BaseModel):
    domain_name: str


@router.post("/")
async def whois_lookup(data: WhoisLookupRequest):
    service = WhoisService()
    result = await service.lookup(data.domain_name)
    return {
        "domain_name": result.domain_name,
        "registrar": result.registrar,
        "creation_date": str(result.creation_date) if result.creation_date else None,
        "expiration_date": str(result.expiration_date) if result.expiration_date else None,
        "updated_date": str(result.updated_date) if result.updated_date else None,
        "nameservers": result.nameservers,
        "status": result.status,
        "dnssec": result.dnssec,
    }
