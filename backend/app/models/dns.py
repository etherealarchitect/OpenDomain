import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class RecordType(enum.StrEnum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    SRV = "SRV"
    CAA = "CAA"
    PTR = "PTR"
    SOA = "SOA"
    ALIAS = "ALIAS"
    TLSA = "TLSA"
    DS = "DS"
    DNSKEY = "DNSKEY"


class DnsZone(Base):
    __tablename__ = "dns_zones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domains.id"), unique=True, nullable=False
    )
    zone_name: Mapped[str] = mapped_column(String(253), unique=True, nullable=False)

    primary_ns: Mapped[str] = mapped_column(String(253), default="ns1.opendomain.local", nullable=False)
    admin_email: Mapped[str] = mapped_column(String(253), default="admin.opendomain.local", nullable=False)
    serial: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    refresh: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)
    retry: Mapped[int] = mapped_column(Integer, default=900, nullable=False)
    expire: Mapped[int] = mapped_column(Integer, default=604800, nullable=False)
    minimum_ttl: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    default_ttl: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)

    dnssec_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dnssec_algorithm: Mapped[str | None] = mapped_column(String(50))
    dnssec_ds_record: Mapped[str | None] = mapped_column(Text)

    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    domain = relationship("Domain", back_populates="dns_zone")
    records = relationship("DnsRecord", back_populates="zone", cascade="all, delete-orphan", lazy="selectin")


class DnsRecord(Base):
    __tablename__ = "dns_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dns_zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    record_type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False)
    name: Mapped[str] = mapped_column(String(253), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ttl: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)
    priority: Mapped[int | None] = mapped_column(Integer)
    proxied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    zone = relationship("DnsZone", back_populates="records")
