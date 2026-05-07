from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.quotation import Quotation


def list_quotations_for_request(*, db: Session, request_id: uuid.UUID) -> list[Quotation]:
    stmt = select(Quotation).where(Quotation.request_id == request_id).order_by(Quotation.created_at)
    return list(db.scalars(stmt).all())

