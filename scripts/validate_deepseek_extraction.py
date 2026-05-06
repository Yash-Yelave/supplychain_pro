from __future__ import annotations

import os
from datetime import date, timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from dotenv import load_dotenv

from app.db.session import SessionLocal
from app.extraction.pipeline.quotation_pipeline import QuotationExtractor, extract_and_store_quotation
from app.extraction.services.deepseek_client import DeepSeekChatClient
from app.models.procurement_request import ProcurementRequest
from app.models.supplier import Supplier


TEST_CASES: list[tuple[str, str]] = [
    (
        "clean supplier quotation",
        "Supplier: Shree BuildMat Traders\nMaterial: cement\nRate: INR 402.50\nMOQ: 100\nDelivery: 3 days\nValidity: 7 days\nPayment: Net 7 days",
    ),
    (
        "messy quotation",
        "hi,\n  rate - inr402.50 (cement)  \nMOQ:100 bags  delivery :3days\nvalidity 7d\npaymnt: net7\nthx",
    ),
    (
        "incomplete quotation",
        "We can supply cement. Delivery 5-7 days. Please confirm required qty and location.",
    ),
    (
        "noisy/unstructured quotation",
        "RE: Quotation\nCement OPC 53 grade available.\nRATE - INR 399.00\n*subject to stock*\nMOQ: 200\nDelivery: 2 days (city)\nValidity: 3 days\nPayment: 50% advance, bal on delivery\nNote: GST extra.\n--\nSent from phone",
    ),
    (
        "short supplier reply",
        "Ok. Rate INR 410. Delivery 7 days.",
    ),
]


def _can_use_llm() -> bool:
    return bool(os.getenv("DEEPSEEK_API_KEY", "").strip())


def main() -> int:
    load_dotenv(override=False)
    if not _can_use_llm():
        print("Missing DEEPSEEK_API_KEY. Set it in .env to run real DeepSeek validation.")
        return 2

    llm = DeepSeekChatClient()
    extractor = QuotationExtractor(llm=llm)

    db_ok = True
    db = None
    req_id = None
    supplier_id = None
    try:
        db = SessionLocal()
        supplier_id = db.scalar(select(Supplier.id).order_by(Supplier.created_at.asc()).limit(1))
        req = ProcurementRequest(
            material_type="cement",
            quantity=100,
            unit="bag",
            deadline=date.today() + timedelta(days=7),
            status="pending",
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        req_id = req.id
    except SQLAlchemyError as e:
        db_ok = False
        print("DB persistence: SKIPPED (database connection failed)")
        print(f"DB error: {e}")
        if db is not None:
            db.close()
            db = None

    try:
        for name, raw in TEST_CASES:
            print("\n===", name.upper(), "===")
            print("RAW:\n", raw)

            result = extractor.extract(raw_text=raw, supplier_hint=None, material_hint="cement")
            print("EXTRACTED:", result.extracted.model_dump())
            print("CONFIDENCE:", result.extraction_confidence)
            print("MISSING:", result.missing_fields)

            if db_ok and db is not None and req_id is not None and supplier_id is not None:
                try:
                    q, _ = extract_and_store_quotation(
                        db=db,
                        request_id=req_id,
                        supplier_id=supplier_id,
                        raw_text=raw,
                        supplier_hint=None,
                        material_hint="cement",
                        llm=llm,
                    )
                    if q is None:
                        print("DB: not inserted (missing required fields like unit_price/currency)")
                    else:
                        print("DB: inserted quotation id:", q.id)
                        print("DB: notes:", q.notes)
                        print("DB: confidence:", q.extraction_confidence)
                        print("DB: missing_fields:", q.missing_fields)
                except SQLAlchemyError as e:
                    print("DB: insert failed:", e)

        return 0
    finally:
        extractor.close()
        if db is not None:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
