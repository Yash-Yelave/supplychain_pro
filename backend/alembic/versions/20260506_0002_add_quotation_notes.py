"""add quotation notes

Revision ID: 20260506_0002
Revises: 20260505_0001
Create Date: 2026-05-06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260506_0002"
down_revision: str | None = "20260505_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("quotations", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("quotations", "notes")

