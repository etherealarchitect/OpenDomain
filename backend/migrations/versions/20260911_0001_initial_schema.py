"""Create the initial OpenDomain application schema.

Revision ID: 20260911_0001
Revises:
Create Date: 2026-09-11
"""

from alembic import op
from backend.app import models  # noqa: F401
from backend.app.core.database import Base

# revision identifiers, used by Alembic.
revision = "20260911_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This first revision provisions the historical application schema only.
    # Authentication lifecycle tables and columns are introduced separately so
    # an existing installation can upgrade deterministically.
    tables = [
        table
        for name, table in Base.metadata.tables.items()
        if name
        not in {
            "auth_audit_events",
            "auth_challenges",
            "auth_sessions",
            "auth_tokens",
            "backup_codes",
        }
    ]
    Base.metadata.create_all(bind=op.get_bind(), tables=tables, checkfirst=True)


def downgrade() -> None:
    tables = [
        table
        for name, table in Base.metadata.tables.items()
        if name
        not in {
            "auth_audit_events",
            "auth_challenges",
            "auth_sessions",
            "auth_tokens",
            "backup_codes",
        }
    ]
    Base.metadata.drop_all(bind=op.get_bind(), tables=tables, checkfirst=True)
