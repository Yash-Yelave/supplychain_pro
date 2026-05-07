from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.procurement_requests import set_request_agent_and_status
from app.crud.trust_scores import upsert_trust_score
from app.models.procurement_request import ProcurementRequestStatus
from app.procurement.scoring import TrustScoreWeights, compute_trust_scores
from app.procurement.state import PipelineStatus, ProcurementState, TrustScoreBreakdown


def scoring_agent(state: ProcurementState, *, db: Session, weights: TrustScoreWeights | None = None) -> ProcurementState:
    if state.request_id is None:
        raise RuntimeError("Missing request_id in state (supervisor did not run)")

    state.active_agent = "scoring"
    state.status = PipelineStatus.scoring
    state.log(agent="scoring", event="start")
    set_request_agent_and_status(db=db, request_id=state.request_id, agent="scoring", status=ProcurementRequestStatus.in_progress)

    supplier_ids = [s.id for s in state.suppliers]
    supplier_response_hours = {s.id: int(s.simulated_response_hours) for s in state.suppliers}
    supplier_referrals = {s.id: int(s.referral_count) for s in state.suppliers}
    supplier_unit_prices = {q.supplier_id: float(q.unit_price) for q in state.extracted_quotations if q.unit_price is not None}
    supplier_missing_fields = {q.supplier_id: list(q.missing_fields) for q in state.extracted_quotations}
    supplier_conf = {q.supplier_id: float(q.extraction_confidence) for q in state.extracted_quotations}

    scores = compute_trust_scores(
        supplier_ids=supplier_ids,
        supplier_response_hours=supplier_response_hours,
        supplier_referrals=supplier_referrals,
        supplier_unit_prices=supplier_unit_prices,
        supplier_missing_fields=supplier_missing_fields,
        supplier_extraction_confidence=supplier_conf,
        weights=weights,
        core_field_count=8,
    )

    state.trust_scores = []
    for sid in supplier_ids:
        row = scores[sid]
        ts = upsert_trust_score(
            db=db,
            request_id=state.request_id,
            supplier_id=sid,
            price_competitiveness=row["price_competitiveness"],
            response_speed_score=row["response_speed_score"],
            quote_completeness=row["quote_completeness"],
            referral_score=row["referral_score"],
            composite_score=row["composite_score"],
            weights_used=row["weights_used"],
        )
        state.trust_scores.append(
            TrustScoreBreakdown(
                supplier_id=sid,
                trust_score_id=ts.id,
                price_competitiveness=row["price_competitiveness"],
                response_speed_score=row["response_speed_score"],
                quote_completeness=row["quote_completeness"],
                referral_score=row["referral_score"],
                composite_score=row["composite_score"],
                weights_used=row["weights_used"],
            )
        )

    state.log(agent="scoring", event="trust_scores_persisted", count=len(state.trust_scores))
    state.status = PipelineStatus.analyzing
    state.log(agent="scoring", event="handoff", next_agent="analyst")
    return state

