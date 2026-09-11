"""Add explicit secure authentication lifecycle schema.

Revision ID: 20260911_0002
Revises: 20260911_0001
Create Date: 2026-09-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260911_0002"
down_revision = "20260911_0001"
branch_labels = None
depends_on = None

user_role = postgresql.ENUM("user", "admin", "reseller", name="userrole", create_type=False)
auth_token_purpose = postgresql.ENUM(
    "email_verification", "password_reset", name="authtokenpurpose", create_type=False
)
auth_challenge_purpose = postgresql.ENUM(
    "mfa_login", "mfa_enrollment", name="authchallengepurpose", create_type=False
)


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    auth_token_purpose.create(bind, checkfirst=True)
    auth_challenge_purpose.create(bind, checkfirst=True)

    if not _has_column("users", "is_verified"):
        op.add_column(
            "users",
            sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    if not _has_column("users", "two_factor_enabled"):
        op.add_column(
            "users",
            sa.Column(
                "two_factor_enabled", sa.Boolean(), nullable=False, server_default=sa.false()
            ),
        )
    if not _has_column("users", "two_factor_secret"):
        op.add_column("users", sa.Column("two_factor_secret", sa.Text(), nullable=True))
    if not _has_column("users", "last_totp_counter"):
        op.add_column("users", sa.Column("last_totp_counter", sa.Integer(), nullable=True))

    op.create_table(
        "auth_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("purpose", auth_token_purpose, nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_tokens_user_id", "auth_tokens", ["user_id"])
    op.create_index("ix_auth_tokens_purpose", "auth_tokens", ["purpose"])
    op.create_index("ix_auth_tokens_token_hash", "auth_tokens", ["token_hash"])
    op.create_index("ix_auth_tokens_expires_at", "auth_tokens", ["expires_at"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_token_hash", "auth_sessions", ["token_hash"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])

    op.create_table(
        "auth_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("purpose", auth_challenge_purpose, nullable=False),
        sa.Column("secret_encrypted", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_challenges_user_id", "auth_challenges", ["user_id"])
    op.create_index("ix_auth_challenges_purpose", "auth_challenges", ["purpose"])
    op.create_index("ix_auth_challenges_expires_at", "auth_challenges", ["expires_at"])

    op.create_table(
        "backup_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_backup_codes_user_id", "backup_codes", ["user_id"])

    op.create_table(
        "auth_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_audit_events_user_id", "auth_audit_events", ["user_id"])
    op.create_index("ix_auth_audit_events_event_type", "auth_audit_events", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_auth_audit_events_event_type", table_name="auth_audit_events")
    op.drop_index("ix_auth_audit_events_user_id", table_name="auth_audit_events")
    op.drop_table("auth_audit_events")
    op.drop_index("ix_backup_codes_user_id", table_name="backup_codes")
    op.drop_table("backup_codes")
    op.drop_index("ix_auth_challenges_expires_at", table_name="auth_challenges")
    op.drop_index("ix_auth_challenges_purpose", table_name="auth_challenges")
    op.drop_index("ix_auth_challenges_user_id", table_name="auth_challenges")
    op.drop_table("auth_challenges")
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_token_hash", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_index("ix_auth_tokens_expires_at", table_name="auth_tokens")
    op.drop_index("ix_auth_tokens_token_hash", table_name="auth_tokens")
    op.drop_index("ix_auth_tokens_purpose", table_name="auth_tokens")
    op.drop_index("ix_auth_tokens_user_id", table_name="auth_tokens")
    op.drop_table("auth_tokens")
    op.drop_column("users", "last_totp_counter")
    op.drop_column("users", "two_factor_secret")
    op.drop_column("users", "two_factor_enabled")
    op.drop_column("users", "is_verified")
    op.execute("DROP TYPE IF EXISTS authchallengepurpose")
    op.execute("DROP TYPE IF EXISTS authtokenpurpose")
