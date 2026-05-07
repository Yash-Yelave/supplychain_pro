from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.extraction.pipeline.quotation_pipeline import QuotationExtractor
from app.extraction.schemas.quotation import QuotationExtractionResult
from app.extraction.services.deepseek_client import DeepSeekChatClient
from app.models.quotation import Quotation


def extract_and_build_quotation(
    *,
    db: Session,
    request_id,
    supplier_id,
    raw_text: str,
    supplier_hint: str | None = None,
    material_hint: str | None = None,
    llm: DeepSeekChatClient | None = None,
) -> tuple[Quotation | None, QuotationExtractionResult]:
    """
    Like `extract_and_store_quotation`, but does not commit.

    This is used by the LangGraph pipeline to minimize DB round-trips and keep
    one transaction boundary per workflow step.
    """

    extractor = QuotationExtractor(llm=llm) if llm is not None else QuotationExtractor()
    try:
        result = extractor.extract(raw_text=raw_text, supplier_hint=supplier_hint, material_hint=material_hint)
    finally:
        if llm is None:
            extractor.close()

    extracted = result.extracted
    if extracted.unit_price is None or not extracted.currency:
        return None, result

    q = Quotation(
        request_id=request_id,
        supplier_id=supplier_id,
        unit_price=Decimal(extracted.unit_price),
        currency=str(extracted.currency).upper(),
        moq=extracted.minimum_order_quantity,
        delivery_days=extracted.delivery_days,
        validity_days=extracted.validity_days,
        payment_terms=extracted.payment_terms,
        notes=extracted.notes,
        extraction_confidence=Decimal(str(result.extraction_confidence)).quantize(Decimal("0.0001")),
        missing_fields=result.missing_fields,
        raw_text=raw_text,
    )
    db.add(q)
    db.flush()
    return q, result

