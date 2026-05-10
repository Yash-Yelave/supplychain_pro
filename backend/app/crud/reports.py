from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report


def upsert_report(
    *,
    db: Session,
    request_id: uuid.UUID,
    summary_text: str,
    top_suppliers: list[dict],
) -> Report:
    stmt = select(Report).where(Report.request_id == request_id)
    existing = db.scalar(stmt)
    row = existing or Report(request_id=request_id, summary_text=summary_text, top_suppliers=top_suppliers)
    row.summary_text = summary_text
    row.top_suppliers = top_suppliers
    if existing is None:
        db.add(row)
    db.flush()
    return row

