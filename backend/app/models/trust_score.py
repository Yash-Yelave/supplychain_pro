import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrustScore(Base):
    __tablename__ = "trust_scores"
    __table_args__ = (UniqueConstraint("request_id", "supplier_id", name="uq_trust_scores_request_supplier"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procurement_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    price_competitiveness: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    response_speed_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    quote_completeness: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    referral_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    composite_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, index=True)
    weights_used: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    score_analysis: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    request = relationship("ProcurementRequest", back_populates="trust_scores")
    supplier = relationship("Supplier", back_populates="trust_scores")
