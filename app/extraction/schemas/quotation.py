from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


CurrencyCode = Literal["INR", "USD", "EUR", "GBP", "AED", "SAR", "SGD", "AUD", "CAD"]


class QuotationExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supplier_name: str | None = Field(default=None, max_length=255)
    material_type: str | None = Field(default=None, max_length=100)
    unit_price: Decimal | None = Field(default=None)
    currency: CurrencyCode | str | None = Field(default=None, max_length=8)
    minimum_order_quantity: int | None = Field(default=None, ge=1)
    delivery_days: int | None = Field(default=None, ge=0)
    validity_days: int | None = Field(default=None, ge=0)
    payment_terms: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("supplier_name", "material_type", "payment_terms", "notes", mode="before")
    @classmethod
    def _strip_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    @field_validator("currency", mode="before")
    @classmethod
    def _normalize_currency(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip().upper()
            return v or None
        return v

    @field_validator("unit_price", mode="before")
    @classmethod
    def _coerce_decimal(cls, v: Any) -> Any:
        if v is None or v == "":
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            cleaned = v.strip().replace(",", "")
            if cleaned == "":
                return None
            return Decimal(cleaned)
        return v

    @field_validator("unit_price")
    @classmethod
    def _unit_price_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is None:
            return None
        if v <= 0:
            raise ValueError("unit_price must be > 0")
        return v


class QuotationExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extracted: QuotationExtraction
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    missing_fields: list[str] = Field(default_factory=list)

