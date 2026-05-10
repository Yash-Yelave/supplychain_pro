import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    material_categories: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    simulated_response_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    referral_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    simulated_reply_template: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    quotations = relationship("Quotation", back_populates="supplier", cascade="all, delete-orphan")
    trust_scores = relationship("TrustScore", back_populates="supplier", cascade="all, delete-orphan")
