from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.procurement_requests import set_request_agent_and_status
from app.crud.suppliers import get_suppliers_by_category
from app.models.procurement_request import ProcurementRequestStatus
from app.procurement.state import PipelineStatus, ProcurementState, SupplierSnapshot


def discovery_agent(state: ProcurementState, *, db: Session) -> ProcurementState:
    if state.request_id is None:
        raise RuntimeError("Missing request_id in state (supervisor did not run)")

    state.active_agent = "discovery"
    state.status = PipelineStatus.discovering
    state.log(agent="discovery", event="start")
    set_request_agent_and_status(db=db, request_id=state.request_id, agent="discovery", status=ProcurementRequestStatus.in_progress)

    suppliers = get_suppliers_by_category(state.request.material_type, db=db)
    state.suppliers = [
        SupplierSnapshot(
            id=s.id,
            name=s.name,
            email=s.email,
            location=s.location,
            material_categories=list(s.material_categories),
            simulated_response_hours=int(s.simulated_response_hours),
            referral_count=int(s.referral_count),
            simulated_reply_template=s.simulated_reply_template,
        )
        for s in suppliers
    ]

    state.log(agent="discovery", event="suppliers_found", count=len(state.suppliers))
    if not state.suppliers:
        state.status = PipelineStatus.failed
        state.log(agent="discovery", event="no_suppliers", material_type=state.request.material_type)
        raise RuntimeError(f"No suppliers for category: {state.request.material_type}")

    state.status = PipelineStatus.extracting
    state.log(agent="discovery", event="handoff", next_agent="extraction")
    return state
