import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class DomainStatus(enum.StrEnum):
    PENDING_CREATE = "pendingCreate"
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING_TRANSFER = "pendingTransfer"
    PENDING_DELETE = "pendingDelete"
    SUSPENDED = "suspended"
    REDEMPTION = "redemption"
    PENDING_RENEW = "pendingRenew"


class DomainEventType(enum.StrEnum):
    REGISTERED = "registered"
    RENEWED = "renewed"
    TRANSFERRED_IN = "transferred_in"
    TRANSFERRED_OUT = "transferred_out"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    DNS_UPDATED = "dns_updated"
    CONTACT_UPDATED = "contact_updated"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    PRIVACY_ENABLED = "privacy_enabled"
    PRIVACY_DISABLED = "privacy_disabled"
    AUTO_RENEW_ENABLED = "auto_renew_enabled"
    AUTO_RENEW_DISABLED = "auto_renew_disabled"


class TransferStatus(enum.StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(253), unique=True, index=True, nullable=False)
    tld: Mapped[str] = mapped_column(String(63), index=True, nullable=False)
    status: Mapped[DomainStatus] = mapped_column(
        Enum(DomainStatus), default=DomainStatus.PENDING_CREATE, nullable=False
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    registrant_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id")
    )
    admin_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id")
    )
    tech_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id")
    )
    billing_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id")
    )

    nameservers: Mapped[str | None] = mapped_column(Text)
    registry_domain_id: Mapped[str | None] = mapped_column(String(255))
    epp_auth_code: Mapped[str | None] = mapped_column(Text)

    auto_renew: Mapped[bool] = mapped_column(default=True, nullable=False)
    privacy_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    locked: Mapped[bool] = mapped_column(default=True, nullable=False)

    registration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_renewed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    registration_period_years: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    renewal_price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    owner = relationship("User", back_populates="domains")
    registrant_contact = relationship("Contact", foreign_keys=[registrant_contact_id])
    admin_contact = relationship("Contact", foreign_keys=[admin_contact_id])
    tech_contact = relationship("Contact", foreign_keys=[tech_contact_id])
    billing_contact = relationship("Contact", foreign_keys=[billing_contact_id])
    dns_zone = relationship("DnsZone", back_populates="domain", uselist=False, lazy="selectin")
    events = relationship("DomainEvent", back_populates="domain", order_by="DomainEvent.created_at.desc()")
    transfers = relationship("DomainTransfer", back_populates="domain")


class DomainEvent(Base):
    __tablename__ = "domain_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True
    )
    event_type: Mapped[DomainEventType] = mapped_column(Enum(DomainEventType), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    domain = relationship("Domain", back_populates="events")


class DomainTransfer(Base):
    __tablename__ = "domain_transfers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False
    )
    from_registrar: Mapped[str | None] = mapped_column(String(255))
    to_registrar: Mapped[str | None] = mapped_column(String(255))
    auth_code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TransferStatus] = mapped_column(
        Enum(TransferStatus), default=TransferStatus.PENDING, nullable=False
    )
    initiated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    initiated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    domain = relationship("Domain", back_populates="transfers")
