import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.dns import DnsRecord, DnsZone, RecordType
from backend.app.models.domain import Domain
from backend.app.schemas.dns import DnsRecordCreate, DnsRecordUpdate, DnsZoneExport

DNS_TEMPLATES = {
    "github-pages": [
        DnsRecordCreate(record_type="A", name="@", content="185.199.108.153", ttl=3600),
        DnsRecordCreate(record_type="A", name="@", content="185.199.109.153", ttl=3600),
        DnsRecordCreate(record_type="A", name="@", content="185.199.110.153", ttl=3600),
        DnsRecordCreate(record_type="A", name="@", content="185.199.111.153", ttl=3600),
        DnsRecordCreate(record_type="CNAME", name="www", content="{user}.github.io", ttl=3600),
    ],
    "google-workspace": [
        DnsRecordCreate(record_type="MX", name="@", content="aspmx.l.google.com", priority=1, ttl=3600),
        DnsRecordCreate(record_type="MX", name="@", content="alt1.aspmx.l.google.com", priority=5, ttl=3600),
        DnsRecordCreate(record_type="MX", name="@", content="alt2.aspmx.l.google.com", priority=5, ttl=3600),
        DnsRecordCreate(record_type="TXT", name="@", content="v=spf1 include:_spf.google.com ~all", ttl=3600),
    ],
    "microsoft-365": [
        DnsRecordCreate(record_type="MX", name="@", content="{domain}.mail.protection.outlook.com", priority=0, ttl=3600),
        DnsRecordCreate(record_type="TXT", name="@", content="v=spf1 include:spf.protection.outlook.com -all", ttl=3600),
        DnsRecordCreate(record_type="CNAME", name="autodiscover", content="autodiscover.outlook.com", ttl=3600),
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


class DnsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _verify_domain_ownership(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> Domain:
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        )
        domain = result.scalar_one_or_none()
        if not domain:
            raise ValueError("Domain not found or access denied")
        return domain

    async def get_zone(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> DnsZone | None:
        await self._verify_domain_ownership(domain_id, user_id)
        result = await self.db.execute(select(DnsZone).where(DnsZone.domain_id == domain_id))
        return result.scalar_one_or_none()

    async def get_or_create_zone(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> DnsZone:
        domain = await self._verify_domain_ownership(domain_id, user_id)
        result = await self.db.execute(select(DnsZone).where(DnsZone.domain_id == domain_id))
        zone = result.scalar_one_or_none()

        if not zone:
            zone = DnsZone(domain_id=domain_id, zone_name=domain.name)
            self.db.add(zone)
            await self.db.flush()

            default_records = [
                DnsRecord(zone_id=zone.id, record_type=RecordType.NS, name="@", content="ns1.opendomain.local"),
                DnsRecord(zone_id=zone.id, record_type=RecordType.NS, name="@", content="ns2.opendomain.local"),
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

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
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
            lines.append(f"{record.name} {record.ttl} IN {record.record_type}{priority_str} {record.content}")

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
                content = " ".join(parts[idx + 1:])

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
            raise ValueError(f"Unknown template: {template_name}. Available: {', '.join(DNS_TEMPLATES)}")

        records_data = []
        for record_template in template:
            content = record_template.content
            for key, value in params.items():
                content = content.replace(f"{{{key}}}", value)
            records_data.append(DnsRecordCreate(
                record_type=record_template.record_type,
                name=record_template.name,
                content=content,
                ttl=record_template.ttl,
                priority=record_template.priority,
            ))

        await self.create_records_bulk(domain_id, records_data, user_id)
        zone = await self.get_or_create_zone(domain_id, user_id)
        await self.db.refresh(zone)
        return zone
