from __future__ import annotations

import os
from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud.procurement_requests import set_request_agent_and_status
from app.extraction.pipeline.store import extract_and_build_quotation
from app.extraction.simulation.quote_generator import generate_supplier_quote
from app.extraction.services.deepseek_client import DeepSeekChatClient
from app.models.procurement_request import ProcurementRequestStatus
from app.models.quotation import Quotation
from app.procurement.state import ExtractedQuotation, PipelineStatus, ProcurementState, SimulatedQuotation


def extraction_agent(state: ProcurementState, *, db: Session) -> ProcurementState:
    if state.request_id is None:
        raise RuntimeError("Missing request_id in state (supervisor did not run)")

    state.active_agent = "extraction"
    state.status = PipelineStatus.extracting
    state.log(agent="extraction", event="start")
    set_request_agent_and_status(db=db, request_id=state.request_id, agent="extraction", status=ProcurementRequestStatus.in_progress)

    use_llm = bool(os.getenv("DEEPSEEK_API_KEY", "").strip())
    llm = DeepSeekChatClient() if use_llm else None
    if use_llm:
        state.log(agent="extraction", event="llm_enabled", provider="deepseek")
    else:
        state.log(agent="extraction", event="llm_disabled", reason="missing_DEEPSEEK_API_KEY")

    try:
        state.simulated_quotations = []
        state.extracted_quotations = []

        for i, supplier in enumerate(state.suppliers):
            sim = generate_supplier_quote(supplier=_supplier_like(supplier), material_type=state.request.material_type, seed=1000 + i)
            state.simulated_quotations.append(
                SimulatedQuotation(
                    supplier_id=uuid_from(sim.supplier_id),
                    supplier_name=sim.supplier_name,
                    raw_text=sim.raw_text,
                )
            )

            raw_text = sim.raw_text
            supplier_id = uuid_from(sim.supplier_id)

            q: Quotation | None = None
            confidence: float = 0.0
            missing_fields: list[str] = []

            if use_llm and llm is not None:
                q, result = extract_and_build_quotation(
                    db=db,
                    request_id=state.request_id,
                    supplier_id=supplier_id,
                    raw_text=raw_text,
                    supplier_hint=sim.supplier_name,
                    material_hint=state.request.material_type,
                    llm=llm,
                )
                confidence = float(result.extraction_confidence)
                missing_fields = list(result.missing_fields)

            if q is None:
                # Deterministic fallback: persist the structured simulated values.
                q = Quotation(
                    request_id=state.request_id,
                    supplier_id=supplier_id,
                    unit_price=Decimal(str(sim.unit_price)).quantize(Decimal("0.01")),
                    currency=str(sim.currency).upper(),
                    moq=sim.moq,
                    delivery_days=sim.delivery_days,
                    validity_days=sim.validity_days,
                    payment_terms=sim.payment_terms,
                    notes="simulation_fallback",
                    extraction_confidence=Decimal(str(confidence or 0.25)).quantize(Decimal("0.0001")),
                    missing_fields=missing_fields,
                    raw_text=raw_text,
                )
                db.add(q)
                db.flush()

            state.extracted_quotations.append(
                ExtractedQuotation(
                    supplier_id=supplier_id,
                    quotation_id=q.id,
                    unit_price=q.unit_price,
                    currency=q.currency,
                    moq=q.moq,
                    delivery_days=q.delivery_days,
                    validity_days=q.validity_days,
                    payment_terms=q.payment_terms,
                    notes=q.notes,
                    extraction_confidence=float(confidence or (q.extraction_confidence or 0)),
                    missing_fields=list(q.missing_fields or []),
                )
            )

        state.log(agent="extraction", event="quotations_persisted", count=len(state.extracted_quotations))
        state.status = PipelineStatus.scoring
        state.log(agent="extraction", event="handoff", next_agent="scoring")
        return state
    finally:
        if llm is not None:
            llm.close()


def uuid_from(v: str):
    import uuid

    return uuid.UUID(str(v))


def _supplier_like(snapshot):
    """
    Adapter for `generate_supplier_quote` which expects an ORM `Supplier`.
    Only fields used by the generator are provided.
    """

    class _S:
        def __init__(self, s):
            self.id = s.id
            self.name = s.name
            self.simulated_reply_template = s.simulated_reply_template

    return _S(snapshot)
