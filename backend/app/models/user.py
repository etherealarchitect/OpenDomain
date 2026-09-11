import enum
import uuid
from datetime import UTC, datetime

from backend.app.core.database import Base
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserRole(enum.StrEnum):
    USER = "user"
    ADMIN = "admin"
    RESELLER = "reseller"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    two_factor_secret: Mapped[str | None] = mapped_column(Text)
    last_totp_counter: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    domains = relationship("Domain", back_populates="owner", lazy="selectin")
    contacts = relationship("Contact", back_populates="user", lazy="selectin")
    invoices = relationship("Invoice", back_populates="user", lazy="selectin")

    @property
    def onboarding_state(self) -> str:
        if not self.is_verified:
            return "email_verification_required"
        if not self.two_factor_enabled:
            return "mfa_enrollment_required"
        return "complete"
