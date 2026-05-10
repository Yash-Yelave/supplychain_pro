from __future__ import annotations

import json
from decimal import Decimal

from sqlalchemy.orm import Session

from app.extraction.prompts.quotation_prompt import QUOTATION_SYSTEM_PROMPT, build_quotation_user_prompt
from app.extraction.schemas.quotation import QuotationExtraction, QuotationExtractionResult
from app.extraction.local_extract import local_extract
from app.extraction.services.deepseek_client import DeepSeekChatClient
from app.extraction.validators.quotation_validator import (
    compute_confidence,
    compute_missing_fields,
    quick_reject_text,
)
from app.models.quotation import Quotation


class QuotationExtractor:
    def __init__(self, llm: DeepSeekChatClient | None = None) -> None:
        self._llm = llm or DeepSeekChatClient()

    def close(self) -> None:
        self._llm.close()

    def extract(
        self,
        *,
        raw_text: str,
        supplier_hint: str | None = None,
        material_hint: str | None = None,
    ) -> QuotationExtractionResult:
        debug = bool(__import__("os").getenv("DEEPSEEK_DEBUG", "").strip())
        if quick_reject_text(raw_text):
            extracted = QuotationExtraction(
                supplier_name=supplier_hint,
                material_type=material_hint,
            )
            missing = compute_missing_fields(extracted)
            return QuotationExtractionResult(extracted=extracted, extraction_confidence=0.05, missing_fields=missing)

        # Local extraction first (token-free) to reduce LLM calls and as a fallback.
        local = local_extract(raw_text, supplier_hint=supplier_hint, material_hint=material_hint)
        local_missing = compute_missing_fields(local)
        if debug:
            print("[deepseek][debug] local_extract:", local.model_dump())

        # If we already have the required persistence fields, skip LLM.
        if local.unit_price is not None and local.currency and len(local_missing) <= 5:
            confidence = compute_confidence(local, missing_fields=local_missing, parsed_ok=True)
            return QuotationExtractionResult(extracted=local, extraction_confidence=confidence, missing_fields=local_missing)

        user_prompt = build_quotation_user_prompt(
            raw_text=raw_text,
            supplier_hint=supplier_hint,
            material_hint=material_hint,
        )

        parsed_ok = True
        try:
            payload = self._llm.chat_json(
                system=QUOTATION_SYSTEM_PROMPT,
                user=user_prompt,
                temperature=0.0,
                max_tokens=220,
            )
        except Exception:
            parsed_ok = False
            payload = {}
            if debug:
                import traceback

                print("[deepseek][debug] chat_json failed; falling back to local_extract")
                traceback.print_exc()

        extracted = _coerce_payload(payload, supplier_hint=supplier_hint, material_hint=material_hint)
        # Merge local signal if LLM missed obvious fields.
        if extracted.unit_price is None and local.unit_price is not None:
            extracted.unit_price = local.unit_price
        if not extracted.currency and local.currency:
            extracted.currency = local.currency
        if extracted.minimum_order_quantity is None and local.minimum_order_quantity is not None:
            extracted.minimum_order_quantity = local.minimum_order_quantity
        if extracted.delivery_days is None and local.delivery_days is not None:
            extracted.delivery_days = local.delivery_days
        if extracted.validity_days is None and local.validity_days is not None:
            extracted.validity_days = local.validity_days
        if extracted.payment_terms is None and local.payment_terms is not None:
            extracted.payment_terms = local.payment_terms

        # If LLM failed but local extraction produced useful fields, don't force confidence to 0.
        if not parsed_ok and (extracted.unit_price is not None and extracted.currency):
            parsed_ok = True

        missing = compute_missing_fields(extracted)
        confidence = compute_confidence(extracted, missing_fields=missing, parsed_ok=parsed_ok)
        return QuotationExtractionResult(extracted=extracted, extraction_confidence=confidence, missing_fields=missing)


def extract_and_store_quotation(
    *,
    db: Session,
    request_id,
    supplier_id,
    raw_text: str,
    supplier_hint: str | None = None,
    material_hint: str | None = None,
    llm: DeepSeekChatClient | None = None,
) -> tuple[Quotation | None, QuotationExtractionResult]:
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
    db.commit()
    db.refresh(q)
    return q, result


def _coerce_payload(payload: dict, *, supplier_hint: str | None, material_hint: str | None) -> QuotationExtraction:
    if not isinstance(payload, dict):
        payload = {}

    allowed_keys = {
        "supplier_name",
        "material_type",
        "unit_price",
        "currency",
        "minimum_order_quantity",
        "delivery_days",
        "validity_days",
        "payment_terms",
        "notes",
    }
    cleaned = {k: payload.get(k) for k in allowed_keys}

    if not cleaned.get("supplier_name") and supplier_hint:
        cleaned["supplier_name"] = supplier_hint
    if not cleaned.get("material_type") and material_hint:
        cleaned["material_type"] = material_hint

    try:
        return QuotationExtraction.model_validate(cleaned)
    except Exception:
        # Last-resort: try to recover from "JSON as string" payloads.
        if isinstance(payload, str):
            try:
                return QuotationExtraction.model_validate(json.loads(payload))
            except Exception:
                pass
        return QuotationExtraction(supplier_name=supplier_hint, material_type=material_hint)
