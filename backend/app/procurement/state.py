from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PipelineStatus(str, enum.Enum):
    initialized = "initialized"
    discovering = "discovering"
    extracting = "extracting"
    scoring = "scoring"
    analyzing = "analyzing"
    complete = "complete"
    failed = "failed"


class ProcurementRequestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_type: str = Field(min_length=1, max_length=100)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=50)
    deadline: date


class SupplierSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    name: str
    email: str
    location: str
    material_categories: list[str]
    simulated_response_hours: int
    referral_count: int
    simulated_reply_template: str


class SimulatedQuotation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supplier_id: uuid.UUID
    supplier_name: str
    raw_text: str


class ExtractedQuotation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supplier_id: uuid.UUID
    quotation_id: uuid.UUID | None = None
    unit_price: Decimal | None = None
    currency: str | None = None
    moq: int | None = None
    delivery_days: int | None = None
    validity_days: int | None = None
    payment_terms: str | None = None
    notes: str | None = None
    extraction_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    missing_fields: list[str] = Field(default_factory=list)


class TrustScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supplier_id: uuid.UUID
    trust_score_id: uuid.UUID | None = None
    price_competitiveness: float = Field(ge=0.0, le=1.0)
    response_speed_score: float = Field(ge=0.0, le=1.0)
    quote_completeness: float = Field(ge=0.0, le=1.0)
    referral_score: float = Field(ge=0.0, le=1.0)
    composite_score: float = Field(ge=0.0, le=1.0)
    weights_used: dict[str, float]


class FinalReportSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: uuid.UUID | None = None
    summary_text: str
    top_suppliers: list[dict]


class StateLogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts_utc: datetime
    agent: str
    event: str
    detail: dict = Field(default_factory=dict)


class ProcurementState(BaseModel):
    """
    Shared LangGraph state.

    Intentionally JSON-serializable for logging/debugging.
    """

    model_config = ConfigDict(extra="forbid")

    request: ProcurementRequestInput
    request_id: uuid.UUID | None = None
    status: PipelineStatus = PipelineStatus.initialized
    active_agent: str | None = None

    suppliers: list[SupplierSnapshot] = Field(default_factory=list)
    simulated_quotations: list[SimulatedQuotation] = Field(default_factory=list)
    extracted_quotations: list[ExtractedQuotation] = Field(default_factory=list)
    trust_scores: list[TrustScoreBreakdown] = Field(default_factory=list)

    final_recommendations: list[dict] = Field(default_factory=list)
    final_report: FinalReportSnapshot | None = None

    logs: list[StateLogEntry] = Field(default_factory=list)

    def log(self, *, agent: str, event: str, **detail) -> None:
        self.logs.append(
            StateLogEntry(
                ts_utc=datetime.now(timezone.utc),
                agent=agent,
                event=event,
                detail=detail,
            )
        )
