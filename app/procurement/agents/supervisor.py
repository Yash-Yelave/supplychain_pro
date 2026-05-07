from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.crud.procurement_requests import create_procurement_request, set_request_agent_and_status
from app.models.procurement_request import ProcurementRequestStatus
from app.procurement.state import PipelineStatus, ProcurementState


def supervisor_agent(state: ProcurementState, *, db: Session) -> ProcurementState:
    state.active_agent = "supervisor"
    state.status = PipelineStatus.initialized
    state.log(agent="supervisor", event="start")

    today = datetime.now(timezone.utc).date()
    if state.request.deadline < today:
        state.status = PipelineStatus.failed
        state.log(agent="supervisor", event="invalid_request", reason="deadline_in_past")
        raise ValueError(f"Deadline is in the past: {state.request.deadline}")

    req = create_procurement_request(
        db=db,
        material_type=state.request.material_type,
        quantity=state.request.quantity,
        unit=state.request.unit,
        deadline=state.request.deadline,
    )
    state.request_id = req.id
    set_request_agent_and_status(db=db, request_id=req.id, agent="supervisor", status=ProcurementRequestStatus.in_progress)
    state.log(agent="supervisor", event="request_created", request_id=str(req.id))

    state.status = PipelineStatus.discovering
    state.log(agent="supervisor", event="handoff", next_agent="discovery")
    return state

