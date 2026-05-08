from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.procurement import ProcurementRequestCreate, ProcurementRequestCreateResponse, ProcurementResultsResponse, ProcurementStatusResponse
from app.services.procurement_service import create_request, get_results, get_status, run_pipeline_for_request


router = APIRouter()


@router.post("/request", response_model=ProcurementRequestCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_procurement_request(
    payload: ProcurementRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ProcurementRequestCreateResponse:
    req = create_request(db=db, payload=payload)
    db.commit()
    background_tasks.add_task(run_pipeline_for_request, request_id=req.id, payload=payload)
    return ProcurementRequestCreateResponse(
        request_id=req.id,
        pipeline_status=req.status.value,
        current_agent=req.current_agent,
    )


@router.get("/{request_id}/status", response_model=ProcurementStatusResponse)
def get_procurement_status(request_id: uuid.UUID, db: Session = Depends(get_db)) -> ProcurementStatusResponse:
    return get_status(db=db, request_id=request_id)


@router.get("/{request_id}/results", response_model=ProcurementResultsResponse)
def get_procurement_results(request_id: uuid.UUID, db: Session = Depends(get_db)) -> ProcurementResultsResponse:
    return get_results(db=db, request_id=request_id)
