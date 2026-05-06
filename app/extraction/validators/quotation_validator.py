from __future__ import annotations

from decimal import Decimal

from app.extraction.schemas.quotation import QuotationExtraction
from app.extraction.validators.text import has_any_digit, normalize_quotation_text


CORE_FIELDS: tuple[str, ...] = (
    "supplier_name",
    "material_type",
    "unit_price",
    "currency",
    "minimum_order_quantity",
    "delivery_days",
    "validity_days",
    "payment_terms",
)


def quick_reject_text(raw_text: str) -> bool:
    t = normalize_quotation_text(raw_text)
    if not t:
        return True
    if len(t) < 20:
        return True
    if not has_any_digit(t):
        return True
    return False


def compute_missing_fields(extracted: QuotationExtraction) -> list[str]:
    missing: list[str] = []
    for field in CORE_FIELDS:
        if getattr(extracted, field) in (None, "", []):
            missing.append(field)
    return missing


def compute_confidence(extracted: QuotationExtraction, *, missing_fields: list[str], parsed_ok: bool) -> float:
    if not parsed_ok:
        return 0.0
    total = len(CORE_FIELDS)
    filled = total - len(missing_fields)
    score = 0.25 + 0.75 * (filled / total)

    if extracted.unit_price is None:
        score *= 0.4
    elif isinstance(extracted.unit_price, Decimal) and extracted.unit_price > 0:
        score *= 1.0

    return max(0.0, min(1.0, float(score)))

