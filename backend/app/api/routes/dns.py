import uuid

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.api.routes.auth import enforce_auth_rate_limit
from backend.app.schemas.dns import (
    BulkDnsRecordCreate,
    DnsDiscoveryResponse,
    DnsImportApplyRequest,
    DnsImportPreviewRequest,
    DnsImportPreviewResponse,
    DnsRecordCreate,
    DnsRecordResponse,
    DnsRecordUpdate,
    DnsTemplateApply,
    DnsZoneExport,
    DnsZoneResponse,
)
from backend.app.services.dns_service import DnsRevisionConflictError, DnsService
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/domains/{domain_id}/dns", tags=["dns"])


@router.get("/", response_model=DnsZoneResponse)
async def get_zone(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DnsService(db)
    zone = await service.get_zone(domain_id, current_user.id)
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DNS zone not found")
    return zone


@router.post("/records", response_model=DnsRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    domain_id: uuid.UUID, data: DnsRecordCreate, db: DbSession, current_user: CurrentUser
):
    service = DnsService(db)
    return await service.create_record(domain_id, data, current_user.id)


@router.post(
    "/records/bulk", response_model=list[DnsRecordResponse], status_code=status.HTTP_201_CREATED
)
async def create_records_bulk(
    domain_id: uuid.UUID, data: BulkDnsRecordCreate, db: DbSession, current_user: CurrentUser
):
    service = DnsService(db)
    return await service.create_records_bulk(domain_id, data.records, current_user.id)


@router.patch("/records/{record_id}", response_model=DnsRecordResponse)
async def update_record(
    domain_id: uuid.UUID,
    record_id: uuid.UUID,
    data: DnsRecordUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    service = DnsService(db)
    return await service.update_record(domain_id, record_id, data, current_user.id)


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    domain_id: uuid.UUID, record_id: uuid.UUID, db: DbSession, current_user: CurrentUser
):
    service = DnsService(db)
    await service.delete_record(domain_id, record_id, current_user.id)


@router.get("/export", response_model=DnsZoneExport)
async def export_zone(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = DnsService(db)
    return await service.export_zone_file(domain_id, current_user.id)


@router.post("/import", response_model=DnsZoneResponse)
async def import_zone(
    domain_id: uuid.UUID, zone_file: str, db: DbSession, current_user: CurrentUser
):
    """Legacy BIND import. This appends records; use preview/apply APIs for safe imports."""
    service = DnsService(db)
    return await service.import_zone_file(domain_id, zone_file, current_user.id)


@router.post("/discovery", response_model=DnsDiscoveryResponse)
async def discover_dns(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    """Discover supported public apex DNS records for an owned domain."""
    await enforce_auth_rate_limit("dns-discovery-user", str(current_user.id), 30, 3600)
    discovery = await DnsService(db).discover_records(domain_id, current_user.id)
    return DnsDiscoveryResponse(
        domain_name=discovery.domain_name,
        records=discovery.records,
        queried_types=discovery.queried_types,
        warnings=discovery.warnings,
    )


@router.post("/import-preview", response_model=DnsImportPreviewResponse)
async def preview_dns_import(
    domain_id: uuid.UUID, data: DnsImportPreviewRequest, db: DbSession, current_user: CurrentUser
):
    return await DnsService(db).preview_import(domain_id, data.records, current_user.id)


@router.post("/import-apply", response_model=DnsZoneResponse)
async def apply_dns_import(
    domain_id: uuid.UUID, data: DnsImportApplyRequest, db: DbSession, current_user: CurrentUser
):
    """Apply a reviewed discovery/import using explicit merge or replacement semantics."""
    try:
        return await DnsService(db).apply_import(
            domain_id,
            data.records,
            data.mode,
            data.confirm_replace,
            current_user.id,
            data.expected_revision,
        )
    except DnsRevisionConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/templates")
async def list_templates():
    from backend.app.services.dns_service import DNS_TEMPLATES

    descriptions = {
        "github-pages": "A records and www CNAME for GitHub Pages hosting",
        "google-workspace": "MX records and SPF for Google Workspace email",
        "microsoft-365": "MX, SPF, and autodiscover for Microsoft 365 email",
        "vercel": "A record and www CNAME for Vercel deployments",
        "netlify": "A record and www CNAME for Netlify deployments",
    }
    return [
        {
            "name": name,
            "description": descriptions.get(name, ""),
            "record_count": len(records),
            "params": [
                p.strip("{}")
                for r in records
                for p in r.content.split()
                if p.startswith("{") and p.endswith("}")
            ],
        }
        for name, records in DNS_TEMPLATES.items()
    ]


@router.post("/templates", response_model=DnsZoneResponse)
async def apply_template(
    domain_id: uuid.UUID, data: DnsTemplateApply, db: DbSession, current_user: CurrentUser
):
    service = DnsService(db)
    return await service.apply_template(domain_id, data.template, data.params, current_user.id)
