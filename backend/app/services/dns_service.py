import asyncio
import uuid
from dataclasses import dataclass, field

import dns.asyncresolver
import dns.exception
import dns.resolver
from backend.app.models.dns import DnsRecord, DnsZone, RecordType
from backend.app.models.domain import Domain, DomainEvent, DomainEventType
from backend.app.schemas.dns import (
    DnsImportPreviewResponse,
    DnsRecordCreate,
    DnsRecordUpdate,
    DnsZoneExport,
)
from backend.app.services.dns_import import (
    has_conflict,
    normalize_record,
    record_key,
    record_settings,
    zone_revision,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

DISCOVERABLE_RECORD_TYPES = ("A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA")


@dataclass(frozen=True)
class DiscoveredDnsRecord:
    record_type: str
    name: str
    content: str
    ttl: int
    priority: int | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DnsDiscovery:
    domain_name: str
    records: list[DiscoveredDnsRecord]
    queried_types: list[str]
    warnings: list[str] = field(default_factory=list)


DNS_TEMPLATES = {
    "github-pages": [
        DnsRecordCreate(record_type="A", name="@", content="185.199.108.153", ttl=3600),
        DnsRecordCreate(record_type="A", name="@", content="185.199.109.153", ttl=3600),
        DnsRecordCreate(record_type="A", name="@", content="185.199.110.153", ttl=3600),
        DnsRecordCreate(record_type="A", name="@", content="185.199.111.153", ttl=3600),
        DnsRecordCreate(record_type="CNAME", name="www", content="{user}.github.io", ttl=3600),
    ],
    "google-workspace": [
        DnsRecordCreate(
            record_type="MX", name="@", content="aspmx.l.google.com", priority=1, ttl=3600
        ),
        DnsRecordCreate(
            record_type="MX", name="@", content="alt1.aspmx.l.google.com", priority=5, ttl=3600
        ),
        DnsRecordCreate(
            record_type="MX", name="@", content="alt2.aspmx.l.google.com", priority=5, ttl=3600
        ),
        DnsRecordCreate(
            record_type="TXT", name="@", content="v=spf1 include:_spf.google.com ~all", ttl=3600
        ),
    ],
    "microsoft-365": [
        DnsRecordCreate(
            record_type="MX",
            name="@",
            content="{domain}.mail.protection.outlook.com",
            priority=0,
            ttl=3600,
        ),
        DnsRecordCreate(
            record_type="TXT",
            name="@",
            content="v=spf1 include:spf.protection.outlook.com -all",
            ttl=3600,
        ),
        DnsRecordCreate(
            record_type="CNAME", name="autodiscover", content="autodiscover.outlook.com", ttl=3600
        ),
    ],
    "vercel": [
        DnsRecordCreate(record_type="A", name="@", content="76.76.21.21", ttl=3600),
        DnsRecordCreate(record_type="CNAME", name="www", content="cname.vercel-dns.com", ttl=3600),
    ],
    "netlify": [
        DnsRecordCreate(record_type="A", name="@", content="75.2.60.5", ttl=3600),
        DnsRecordCreate(record_type="CNAME", name="www", content="{site}.netlify.app", ttl=3600),
    ],
}


class DnsRevisionConflictError(ValueError):
    pass


class DnsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _verify_domain_ownership(
        self, domain_id: uuid.UUID, user_id: uuid.UUID, *, lock: bool = False
    ) -> Domain:
        statement = select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        if lock:
            statement = statement.with_for_update()
        result = await self.db.execute(statement)
        domain = result.scalar_one_or_none()
        if not domain:
            raise ValueError("Domain not found or access denied")
        return domain

    async def get_zone(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> DnsZone | None:
        await self._verify_domain_ownership(domain_id, user_id)
        result = await self.db.execute(
            select(DnsZone)
            .where(DnsZone.domain_id == domain_id)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def discover_records(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> DnsDiscovery:
        """Resolve public apex records; DNS cannot enumerate unknown subdomains."""
        domain = await self._verify_domain_ownership(domain_id, user_id)
        resolver = dns.asyncresolver.Resolver()
        resolver.lifetime = 5
        warnings: list[str] = []

        async def resolve(record_type: str) -> list[DiscoveredDnsRecord]:
            try:
                answer = await resolver.resolve(
                    domain.name.rstrip(".") + ".",
                    record_type,
                    raise_on_no_answer=False,
                    search=False,
                )
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                return []
            except (dns.exception.DNSException, OSError) as exc:
                warnings.append(f"{record_type} lookup failed: {type(exc).__name__}")
                return []
            if answer.rrset is None:
                return []
            if answer.rrset.name.to_text().rstrip(".").lower() != domain.name.rstrip(".").lower():
                warnings.append(
                    f"{record_type}: alias-target records omitted to preserve their actual owner"
                )
                return []
            ttl = answer.rrset.ttl
            records: list[DiscoveredDnsRecord] = []
            for index, rdata in enumerate(answer):
                if index >= 50:
                    warnings.append(f"{record_type}: result truncated to 50 records")
                    break
                priority = None
                content = rdata.to_text()
                if record_type == "MX":
                    priority = rdata.preference
                    content = str(rdata.exchange).rstrip(".")
                elif record_type == "SRV":
                    priority = rdata.priority
                    content = f"{rdata.weight} {rdata.port} {str(rdata.target).rstrip('.')}"
                elif record_type in {"NS", "CNAME"}:
                    content = content.rstrip(".")
                records.append(
                    DiscoveredDnsRecord(
                        record_type=record_type,
                        name="@",
                        content=content,
                        ttl=ttl,
                        priority=priority,
                    )
                )
            return records

        record_groups = await asyncio.gather(
            *(resolve(record_type) for record_type in DISCOVERABLE_RECORD_TYPES)
        )
        records = [record for group in record_groups for record in group]
        if not records:
            warnings.append(
                "No supported public apex records were found. "
                "DNS discovery cannot enumerate arbitrary subdomains."
            )
        return DnsDiscovery(
            domain_name=domain.name,
            records=records,
            queried_types=list(DISCOVERABLE_RECORD_TYPES),
            warnings=warnings,
        )

    async def preview_import(
        self, domain_id: uuid.UUID, records_data: list[DnsRecordCreate], user_id: uuid.UUID
    ) -> DnsImportPreviewResponse:
        domain = await self._verify_domain_ownership(domain_id, user_id)
        zone = await self.get_zone(domain_id, user_id)
        normalized = self._normalize_import(records_data, domain.name)
        existing = []
        for record in zone.records if zone else []:
            try:
                canonical = normalize_record(
                    DnsRecordCreate.model_validate(record, from_attributes=True), domain.name
                )
                canonical = canonical.model_copy(update={"enabled": record.enabled})
            except ValueError:
                canonical = record
            existing.append(canonical)
        additions, unchanged, conflicts = [], [], []
        for record in normalized:
            matching = next(
                (other for other in existing if record_key(other) == record_key(record)), None
            )
            if has_conflict(record, existing):
                conflicts.append(record)
            elif matching and record_settings(matching) == record_settings(record):
                unchanged.append(record)
            else:
                additions.append(record)
        return DnsImportPreviewResponse(
            additions=additions,
            unchanged=unchanged,
            conflicts=conflicts,
            normalized_records=normalized,
            revision=zone_revision(zone),
            warnings=[
                "Imports update local storage only; authoritative DNS is not synchronized.",
                "Replacement preserves apex NS, SOA, DNSKEY and DS records.",
            ],
        )

    @staticmethod
    def _normalize_import(
        records_data: list[DnsRecordCreate], domain_name: str
    ) -> list[DnsRecordCreate]:
        if not 1 <= len(records_data) <= 500:
            raise ValueError("Import must contain between 1 and 500 records")
        normalized: list[DnsRecordCreate] = []
        for data in records_data:
            record = normalize_record(data, domain_name)
            if record.record_type == "NS" and record.name == "@":
                continue  # Delegation changes require a separate, provider-aware operation.
            if has_conflict(record, normalized):
                raise ValueError(
                    "Input contains incompatible CNAME records or inconsistent RRset TTLs"
                )
            if record_key(record) not in {record_key(other) for other in normalized}:
                normalized.append(record)
        if not normalized:
            raise ValueError("No importable records; apex NS and DNSSEC records are protected")
        return normalized

    async def apply_import(
        self,
        domain_id: uuid.UUID,
        records_data: list[DnsRecordCreate],
        mode: str,
        confirm_replace: bool,
        user_id: uuid.UUID,
        expected_revision: str,
    ) -> DnsZone:
        if mode not in {"merge", "replace"}:
            raise ValueError("Import mode must be merge or replace")
        if mode == "replace" and not confirm_replace:
            raise ValueError("Replacing DNS records requires confirm_replace=true")
        await self._verify_domain_ownership(domain_id, user_id, lock=True)
        preview = await self.preview_import(domain_id, records_data, user_id)
        if preview.revision != expected_revision:
            raise DnsRevisionConflictError(
                "DNS zone changed; generate a new preview before importing"
            )
        if mode == "merge" and preview.conflicts:
            raise ValueError(
                "Merge conflicts must be resolved before importing; no records were changed"
            )
        zone = await self.get_or_create_zone(domain_id, user_id)
        additions = preview.additions
        if mode == "replace":
            protected_records = [
                record
                for record in zone.records
                if (
                    str(record.record_type) in {"SOA", "DNSKEY", "DS"}
                    or (
                        record.record_type == RecordType.NS
                        and record.name.lower().rstrip(".") in {"@", zone.zone_name.lower()}
                    )
                )
            ]
            if any(
                has_conflict(record, protected_records) for record in preview.normalized_records
            ):
                raise ValueError("Replacement conflicts with protected DNS records")
            for record in list(zone.records):
                if record not in protected_records:
                    await self.db.delete(record)
            additions = preview.normalized_records
        for record in additions:
            self.db.add(
                DnsRecord(
                    zone_id=zone.id,
                    record_type=RecordType(record.record_type),
                    name=record.name,
                    content=record.content,
                    ttl=record.ttl,
                    priority=record.priority,
                    proxied=record.proxied,
                    comment=record.comment,
                )
            )
        zone.serial += 1
        self.db.add(
            DomainEvent(
                domain_id=domain_id,
                actor_id=user_id,
                event_type=DomainEventType.DNS_UPDATED,
                details=(
                    f"Local DNS import: mode={mode}, records={len(additions)}, serial={zone.serial}"
                ),
            )
        )
        await self.db.flush()
        await self.db.refresh(zone)
        return zone

    async def get_or_create_zone(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> DnsZone:
        domain = await self._verify_domain_ownership(domain_id, user_id, lock=True)
        result = await self.db.execute(select(DnsZone).where(DnsZone.domain_id == domain_id))
        zone = result.scalar_one_or_none()

        if not zone:
            zone = DnsZone(domain_id=domain_id, zone_name=domain.name)
            self.db.add(zone)
            await self.db.flush()

            default_records = [
                DnsRecord(
                    zone_id=zone.id,
                    record_type=RecordType.NS,
                    name="@",
                    content="ns1.opendomain.local",
                ),
                DnsRecord(
                    zone_id=zone.id,
                    record_type=RecordType.NS,
                    name="@",
                    content="ns2.opendomain.local",
                ),
            ]
            self.db.add_all(default_records)
            await self.db.flush()
            await self.db.refresh(zone)

        return zone

    async def create_record(
        self, domain_id: uuid.UUID, data: DnsRecordCreate, user_id: uuid.UUID
    ) -> DnsRecord:
        zone = await self.get_or_create_zone(domain_id, user_id)
        record = DnsRecord(
            zone_id=zone.id,
            record_type=RecordType(data.record_type),
            name=data.name,
            content=data.content,
            ttl=data.ttl,
            priority=data.priority,
            proxied=data.proxied,
            comment=data.comment,
        )
        self.db.add(record)
        zone.serial += 1
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def create_records_bulk(
        self, domain_id: uuid.UUID, records_data: list[DnsRecordCreate], user_id: uuid.UUID
    ) -> list[DnsRecord]:
        zone = await self.get_or_create_zone(domain_id, user_id)
        records = []
        for data in records_data:
            record = DnsRecord(
                zone_id=zone.id,
                record_type=RecordType(data.record_type),
                name=data.name,
                content=data.content,
                ttl=data.ttl,
                priority=data.priority,
                proxied=data.proxied,
                comment=data.comment,
            )
            self.db.add(record)
            records.append(record)
        zone.serial += 1
        await self.db.flush()
        for r in records:
            await self.db.refresh(r)
        return records

    async def update_record(
        self, domain_id: uuid.UUID, record_id: uuid.UUID, data: DnsRecordUpdate, user_id: uuid.UUID
    ) -> DnsRecord:
        zone = await self.get_or_create_zone(domain_id, user_id)
        result = await self.db.execute(
            select(DnsRecord).where(DnsRecord.id == record_id, DnsRecord.zone_id == zone.id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("DNS record not found")

        for attribute, value in data.model_dump(exclude_unset=True).items():
            setattr(record, attribute, value)
        zone.serial += 1
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def delete_record(
        self, domain_id: uuid.UUID, record_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        zone = await self.get_or_create_zone(domain_id, user_id)
        result = await self.db.execute(
            select(DnsRecord).where(DnsRecord.id == record_id, DnsRecord.zone_id == zone.id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("DNS record not found")
        await self.db.delete(record)
        zone.serial += 1

    async def export_zone_file(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> DnsZoneExport:
        zone = await self.get_or_create_zone(domain_id, user_id)
        lines = [
            f"$ORIGIN {zone.zone_name}.",
            f"$TTL {zone.default_ttl}",
            f"@ IN SOA {zone.primary_ns}. {zone.admin_email.replace('@', '.')}. (",
            f"    {zone.serial} ; serial",
            f"    {zone.refresh} ; refresh",
            f"    {zone.retry} ; retry",
            f"    {zone.expire} ; expire",
            f"    {zone.minimum_ttl} ; minimum",
            ")",
        ]
        for record in zone.records:
            if not record.enabled:
                continue
            priority_str = f" {record.priority}" if record.priority is not None else ""
            lines.append(
                f"{record.name} {record.ttl} IN {record.record_type}{priority_str} {record.content}"
            )

        return DnsZoneExport(zone_name=zone.zone_name, zone_file="\n".join(lines))

    async def import_zone_file(
        self, domain_id: uuid.UUID, zone_file: str, user_id: uuid.UUID
    ) -> DnsZone:
        zone = await self.get_or_create_zone(domain_id, user_id)
        valid_types = {t.value for t in RecordType} - {"SOA", "DNSKEY"}
        imported = 0

        for line in zone_file.splitlines():
            line = line.strip()
            if not line or line.startswith(";") or line.startswith("$"):
                continue
            if "SOA" in line:
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            name = parts[0]
            idx = 1
            ttl = zone.default_ttl
            if parts[idx].isdigit():
                ttl = int(parts[idx])
                idx += 1
            if idx < len(parts) and parts[idx].upper() == "IN":
                idx += 1
            if idx >= len(parts):
                continue
            rtype = parts[idx].upper()
            idx += 1
            if rtype not in valid_types or idx >= len(parts):
                continue

            priority = None
            content = " ".join(parts[idx:])
            if rtype in ("MX", "SRV") and parts[idx].isdigit():
                priority = int(parts[idx])
                content = " ".join(parts[idx + 1 :])

            record = DnsRecord(
                zone_id=zone.id,
                record_type=RecordType(rtype),
                name=name,
                content=content,
                ttl=ttl,
                priority=priority,
            )
            self.db.add(record)
            imported += 1

        zone.serial += 1
        await self.db.flush()
        await self.db.refresh(zone)
        return zone

    async def apply_template(
        self, domain_id: uuid.UUID, template_name: str, params: dict[str, str], user_id: uuid.UUID
    ) -> DnsZone:
        template = DNS_TEMPLATES.get(template_name)
        if not template:
            raise ValueError(
                f"Unknown template: {template_name}. Available: {', '.join(DNS_TEMPLATES)}"
            )

        records_data = []
        for record_template in template:
            content = record_template.content
            for key, value in params.items():
                content = content.replace(f"{{{key}}}", value)
            records_data.append(
                DnsRecordCreate(
                    record_type=record_template.record_type,
                    name=record_template.name,
                    content=content,
                    ttl=record_template.ttl,
                    priority=record_template.priority,
                )
            )

        await self.create_records_bulk(domain_id, records_data, user_id)
        zone = await self.get_or_create_zone(domain_id, user_id)
        await self.db.refresh(zone)
        return zone
