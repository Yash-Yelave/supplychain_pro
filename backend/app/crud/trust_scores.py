from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trust_score import TrustScore


def upsert_trust_score(
    *,
    db: Session,
    request_id: uuid.UUID,
    supplier_id: uuid.UUID,
    price_competitiveness: float,
    response_speed_score: float,
    quote_completeness: float,
    referral_score: float,
    composite_score: float,
    weights_used: dict[str, float],
    score_analysis: dict[str, str] | None = None,
) -> TrustScore:
    stmt = select(TrustScore).where(TrustScore.request_id == request_id, TrustScore.supplier_id == supplier_id)
    existing = db.scalar(stmt)
    row = existing or TrustScore(request_id=request_id, supplier_id=supplier_id)

    row.price_competitiveness = Decimal(str(price_competitiveness)).quantize(Decimal("0.0001"))
    row.response_speed_score = Decimal(str(response_speed_score)).quantize(Decimal("0.0001"))
    row.quote_completeness = Decimal(str(quote_completeness)).quantize(Decimal("0.0001"))
    row.referral_score = Decimal(str(referral_score)).quantize(Decimal("0.0001"))
    row.composite_score = Decimal(str(composite_score)).quantize(Decimal("0.0001"))
    row.weights_used = weights_used
    if score_analysis is not None:
        row.score_analysis = score_analysis

    if existing is None:
        db.add(row)
    db.flush()
    return row


def list_trust_scores_for_request(*, db: Session, request_id: uuid.UUID) -> list[TrustScore]:
    stmt = select(TrustScore).where(TrustScore.request_id == request_id).order_by(TrustScore.composite_score.desc())
    return list(db.scalars(stmt).all())

