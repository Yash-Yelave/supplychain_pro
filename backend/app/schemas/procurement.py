from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProcurementRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_type: str = Field(min_length=1, max_length=100)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=50)
    shipping_deadline: date
    target_country_code: str = Field(min_length=2, max_length=2)
    quality_grade: str = Field(min_length=1, max_length=50)

class ActiveProcurementRequest(BaseModel):
    id: uuid.UUID
    status: str
    material_type: str
    quantity: float
    unit: str
    target_country_code: str
    quality_grade: str
    created_at: datetime


class ProcurementRequestCreateResponse(BaseModel):
    request_id: uuid.UUID
    pipeline_status: str
    current_agent: str | None


class ProcurementStatusResponse(BaseModel):
    request_id: uuid.UUID
    pipeline_status: str
    current_agent: str | None
    supplier_count: int
    quotation_count: int
    trust_score_count: int
    created_at: datetime
    completed_at: datetime | None


class RankedSupplier(BaseModel):
    rank: int
    supplier_id: str
    supplier_name: str
    location: str
    unit_price: float | None
    currency: str | None
    scores: dict[str, float]
    score_analysis: dict[str, str] | None = None


class TrustScoreRow(BaseModel):
    supplier_id: uuid.UUID
    supplier_name: str | None
    composite_score: Decimal
    price_competitiveness: Decimal
    response_speed_score: Decimal
    quote_completeness: Decimal
    referral_score: Decimal
    score_analysis: dict[str, str] | None = None
    computed_at: datetime


class ExtractedQuotationRow(BaseModel):
    quotation_id: uuid.UUID
    supplier_id: uuid.UUID
    supplier_name: str | None
    unit_price: Decimal
    currency: str
    moq: int | None
    delivery_days: int | None
    validity_days: int | None
    payment_terms: str | None
    notes: str | None
    extraction_confidence: Decimal | None
    missing_fields: list[str]
    created_at: datetime


class ProcurementResultsResponse(BaseModel):
    request_id: uuid.UUID
    pipeline_status: str
    ranked_suppliers: list[RankedSupplier]
    trust_scores: list[TrustScoreRow]
    extracted_quotations: list[ExtractedQuotationRow]
    final_recommendation_report: str | None
    analyst_summary: str | None
