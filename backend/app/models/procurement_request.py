import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProcurementRequestStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    failed = "failed"


class ProcurementRequest(Base):
    __tablename__ = "procurement_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ProcurementRequestStatus] = mapped_column(
        Enum(ProcurementRequestStatus, name="procurement_request_status"),
        nullable=False,
        default=ProcurementRequestStatus.pending,
        server_default=ProcurementRequestStatus.pending.value,
    )
    current_agent: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    quotations = relationship("Quotation", back_populates="request", cascade="all, delete-orphan")
    trust_scores = relationship("TrustScore", back_populates="request", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="request", cascade="all, delete-orphan", uselist=False)
