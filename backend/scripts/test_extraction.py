from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date, timedelta
from decimal import Decimal

from app.crud.suppliers import get_suppliers_by_category
from app.db.session import SessionLocal
from app.extraction.pipeline.quotation_pipeline import QuotationExtractor, extract_and_store_quotation
from app.extraction.simulation.quote_generator import generate_supplier_quote
from app.extraction.services.deepseek_client import DeepSeekChatClient
from app.extraction.validators.text import normalize_quotation_text
from app.models.procurement_request import ProcurementRequest
from app.models.supplier import Supplier


def _heuristic_extract(raw_text: str, *, supplier_hint: str | None, material_hint: str | None) -> dict:
    t = normalize_quotation_text(raw_text).upper()
    currency = "INR" if "INR" in t or "RS" in t or "₹" in raw_text else None

    price = None
    m = re.search(r"(?:INR|RS|₹)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", raw_text, flags=re.I)
    if m:
        price = Decimal(m.group(1).replace(",", ""))
    else:
        m = re.search(r"RATE\s*[:\-]?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", raw_text, flags=re.I)
        if m:
            price = Decimal(m.group(1).replace(",", ""))

    return {
        "supplier_name": supplier_hint,
        "material_type": material_hint,
        "unit_price": str(price) if price else None,
        "currency": currency,
        "minimum_order_quantity": None,
        "delivery_days": None,
        "validity_days": None,
        "payment_terms": None,
        "notes": "heuristic_fallback",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", default="cement")
    parser.add_argument("--cases", type=int, default=5)
    parser.add_argument("--persist", action="store_true", help="Insert quotations into DB (requires LLM success).")
    args = parser.parse_args()

    material_type = args.material.strip().lower()

    db = SessionLocal()
    try:
        suppliers = get_suppliers_by_category(material_type, db=db)
        if not suppliers:
            print(f"No suppliers found for category: {material_type}")
            return 2

        req = ProcurementRequest(
            material_type=material_type,
            quantity=100,
            unit="bag",
            deadline=date.today() + timedelta(days=7),
            status="pending",
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        use_llm = bool(os.getenv("DEEPSEEK_API_KEY", "").strip())
        llm = DeepSeekChatClient() if use_llm else None
        extractor = QuotationExtractor(llm=llm) if use_llm and llm is not None else None
        if use_llm:
            print("LLM: DeepSeek enabled")
        else:
            print("LLM: disabled (set DEEPSEEK_API_KEY to enable). Using heuristic fallback.")

        for i in range(args.cases):
            supplier: Supplier = suppliers[i % len(suppliers)]
            sim = generate_supplier_quote(supplier=supplier, material_type=material_type, seed=100 + i)

            raw = sim.raw_text
            if i == 1:
                raw = raw.replace("payment", "paymnt").replace("terms", "tmrs")
            if i == 2:
                raw = re.sub(r"(?i)(MOQ|minimum order).*", "MOQ: TBD", raw)
            if i == 3:
                raw = re.sub(r"(?i)(INR|RS|₹)\\s*[0-9][0-9,]*(?:\\.[0-9]{1,2})?", "INR __", raw)
            if i == 4:
                raw = "Ok. Can supply. Delivery 7 days. Confirm qty."

            print("\n--- CASE", i + 1, "---")
            print(raw)

            if use_llm and extractor is not None:
                if args.persist:
                    q, result = extract_and_store_quotation(
                        db=db,
                        request_id=req.id,
                        supplier_id=supplier.id,
                        raw_text=raw,
                        supplier_hint=supplier.name,
                        material_hint=material_type,
                        llm=llm,
                    )
                else:
                    result = extractor.extract(raw_text=raw, supplier_hint=supplier.name, material_hint=material_type)
                    q = None
            else:
                payload = _heuristic_extract(raw, supplier_hint=supplier.name, material_hint=material_type)
                print("Heuristic payload:", json.dumps(payload, indent=2))
                continue

            print("Extracted:", result.extracted.model_dump())
            print("Confidence:", result.extraction_confidence)
            print("Missing:", result.missing_fields)
            if q is not None:
                print("Saved quotation id:", q.id)

        if extractor is not None:
            extractor.close()

        req_from_db = db.get(ProcurementRequest, req.id)
        print("\nRequest created:", req.id)
        print("Quotations linked:", len(req_from_db.quotations) if req_from_db else 0)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
