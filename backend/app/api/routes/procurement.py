from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, status

from app.db.session import SessionLocal
from app.schemas.procurement import ProcurementRequestCreate, ProcurementRequestCreateResponse, ProcurementResultsResponse, ProcurementStatusResponse
from app.services.procurement_service import create_request, get_results, get_status, run_pipeline_for_request


router = APIRouter()


@router.post("/request", response_model=ProcurementRequestCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_procurement_request(
    payload: ProcurementRequestCreate,
    background_tasks: BackgroundTasks,
) -> ProcurementRequestCreateResponse:
    db = SessionLocal()
    try:
        req = create_request(db=db, payload=payload)
        db.commit()
        request_id = req.id
        pipeline_status = req.status.value
        current_agent = req.current_agent
    finally:
        db.close()
    background_tasks.add_task(run_pipeline_for_request, request_id=request_id, payload=payload)
    return ProcurementRequestCreateResponse(
        request_id=request_id,
        pipeline_status=pipeline_status,
        current_agent=current_agent,
    )


@router.get("/{request_id}/status", response_model=ProcurementStatusResponse)
def get_procurement_status(request_id: uuid.UUID) -> ProcurementStatusResponse:
    db = SessionLocal()
    try:
        return get_status(db=db, request_id=request_id)
    finally:
        db.close()


@router.get("/{request_id}/results", response_model=ProcurementResultsResponse)
def get_procurement_results(request_id: uuid.UUID) -> ProcurementResultsResponse:
    db = SessionLocal()
    try:
        return get_results(db=db, request_id=request_id)
    finally:
        db.close()
