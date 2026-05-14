from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.crud.procurement_requests import set_request_agent_and_status
from app.crud.reports import upsert_report
from app.models.procurement_request import ProcurementRequestStatus
from app.procurement.state import FinalReportSnapshot, PipelineStatus, ProcurementState


def analyst_agent(state: ProcurementState, *, db: Session, top_n: int = 3) -> ProcurementState:
    if state.request_id is None:
        raise RuntimeError("Missing request_id in state (supervisor did not run)")

    state.active_agent = "analyst"
    state.status = PipelineStatus.analyzing
    state.log(agent="analyst", event="start")
    set_request_agent_and_status(db=db, request_id=state.request_id, agent="analyst", status=ProcurementRequestStatus.in_progress)

    supplier_by_id = {s.id: s for s in state.suppliers}
    quote_by_supplier = {q.supplier_id: q for q in state.extracted_quotations}
    scores_sorted = sorted(state.trust_scores, key=lambda s: s.composite_score, reverse=True)

    top = scores_sorted[: max(1, top_n)]
    top_suppliers: list[dict] = []
    lines: list[str] = []

    lines.append(f"Procurement material: {state.request.material_type} ({state.request.quantity} {state.request.unit})")
    lines.append(f"Deadline: {state.request.shipping_deadline.isoformat()}")
    lines.append("")
    lines.append("Top supplier recommendations:")

    for rank, s in enumerate(top, start=1):
        supplier = supplier_by_id.get(s.supplier_id)
        quote = quote_by_supplier.get(s.supplier_id)
        if supplier is None:
            continue
        unit_price = float(quote.unit_price) if quote and quote.unit_price is not None else None
        currency = quote.currency if quote else None

        reason_bits = [
            f"score={s.composite_score:.3f}",
            f"price_score={s.price_competitiveness:.3f}",
            f"speed_score={s.response_speed_score:.3f}",
            f"complete_score={s.quote_completeness:.3f}",
            f"referral_score={s.referral_score:.3f}",
        ]
        if unit_price is not None and currency:
            reason_bits.insert(1, f"price={unit_price:.2f} {currency}")

        lines.append(f"{rank}. {supplier.name} ({supplier.location}) - " + ", ".join(reason_bits))

        top_suppliers.append(
            {
                "rank": rank,
                "supplier_id": str(supplier.id),
                "supplier_name": supplier.name,
                "location": supplier.location,
                "unit_price": unit_price,
                "currency": currency,
                "scores": {
                    "composite": s.composite_score,
                    "price_competitiveness": s.price_competitiveness,
                    "response_speed": s.response_speed_score,
                    "quote_completeness": s.quote_completeness,
                    "referral": s.referral_score,
                },
            }
        )

    summary_text = "\n".join(lines).strip()
    report = upsert_report(db=db, request_id=state.request_id, summary_text=summary_text, top_suppliers=top_suppliers)

    state.final_recommendations = top_suppliers
    state.final_report = FinalReportSnapshot(report_id=report.id, summary_text=summary_text, top_suppliers=top_suppliers)
    state.log(agent="analyst", event="report_persisted", report_id=str(report.id))

    set_request_agent_and_status(
        db=db,
        request_id=state.request_id,
        agent=None,
        status=ProcurementRequestStatus.complete,
        completed_at=datetime.now(timezone.utc),
    )
    state.status = PipelineStatus.complete
    state.log(agent="analyst", event="complete")
    return state

