"""create foundation tables

Revision ID: 20260505_0001
Revises:
Create Date: 2026-05-05
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260505_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    request_status = postgresql.ENUM("pending", "in_progress", "complete", "failed", name="procurement_request_status")
    request_status.create(op.get_bind(), checkfirst=True)

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "suppliers" not in existing_tables:
        op.create_table(
            "suppliers",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("location", sa.String(length=255), nullable=False),
            sa.Column("material_categories", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("simulated_response_hours", sa.Integer(), nullable=False),
            sa.Column("referral_count", sa.Integer(), nullable=False),
            sa.Column("simulated_reply_template", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_suppliers_email"), "suppliers", ["email"], unique=True)

    if "procurement_requests" not in existing_tables:
        op.create_table(
            "procurement_requests",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("material_type", sa.String(length=100), nullable=False),
            sa.Column("quantity", sa.Float(), nullable=False),
            sa.Column("unit", sa.String(length=50), nullable=False),
            sa.Column("deadline", sa.Date(), nullable=False),
            sa.Column("status", request_status, server_default="pending", nullable=False),
            sa.Column("current_agent", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_procurement_requests_material_type"), "procurement_requests", ["material_type"])

    if "quotations" not in existing_tables:
        op.create_table(
            "quotations",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
            sa.Column("currency", sa.String(length=3), server_default="INR", nullable=False),
            sa.Column("moq", sa.Integer(), nullable=True),
            sa.Column("delivery_days", sa.Integer(), nullable=True),
            sa.Column("validity_days", sa.Integer(), nullable=True),
            sa.Column("payment_terms", sa.String(length=255), nullable=True),
            sa.Column("extraction_confidence", sa.Numeric(precision=5, scale=4), nullable=True),
            sa.Column("missing_fields", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
            sa.Column("raw_text", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["request_id"], ["procurement_requests.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_quotations_request_id"), "quotations", ["request_id"])
        op.create_index(op.f("ix_quotations_supplier_id"), "quotations", ["supplier_id"])

    if "reports" not in existing_tables:
        op.create_table(
            "reports",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("summary_text", sa.Text(), nullable=False),
            sa.Column("top_suppliers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["request_id"], ["procurement_requests.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("request_id"),
        )
        op.create_index(op.f("ix_reports_request_id"), "reports", ["request_id"], unique=True)

    if "trust_scores" not in existing_tables:
        op.create_table(
            "trust_scores",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("price_competitiveness", sa.Numeric(precision=5, scale=4), nullable=False),
            sa.Column("response_speed_score", sa.Numeric(precision=5, scale=4), nullable=False),
            sa.Column("quote_completeness", sa.Numeric(precision=5, scale=4), nullable=False),
            sa.Column("referral_score", sa.Numeric(precision=5, scale=4), nullable=False),
            sa.Column("composite_score", sa.Numeric(precision=5, scale=4), nullable=False),
            sa.Column("weights_used", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["request_id"], ["procurement_requests.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("request_id", "supplier_id", name="uq_trust_scores_request_supplier"),
        )
        op.create_index(op.f("ix_trust_scores_composite_score"), "trust_scores", ["composite_score"])
        op.create_index(op.f("ix_trust_scores_request_id"), "trust_scores", ["request_id"])
        op.create_index(op.f("ix_trust_scores_supplier_id"), "trust_scores", ["supplier_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_trust_scores_supplier_id"), table_name="trust_scores")
    op.drop_index(op.f("ix_trust_scores_request_id"), table_name="trust_scores")
    op.drop_index(op.f("ix_trust_scores_composite_score"), table_name="trust_scores")
    op.drop_table("trust_scores")
    op.drop_index(op.f("ix_reports_request_id"), table_name="reports")
    op.drop_table("reports")
    op.drop_index(op.f("ix_quotations_supplier_id"), table_name="quotations")
    op.drop_index(op.f("ix_quotations_request_id"), table_name="quotations")
    op.drop_table("quotations")
    op.drop_index(op.f("ix_procurement_requests_material_type"), table_name="procurement_requests")
    op.drop_table("procurement_requests")
    op.drop_index(op.f("ix_suppliers_email"), table_name="suppliers")
    op.drop_table("suppliers")
    postgresql.ENUM(name="procurement_request_status").drop(op.get_bind(), checkfirst=True)
