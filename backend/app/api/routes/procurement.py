from __future__ import annotations

import traceback
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.db.session import SessionLocal
from app.schemas.procurement import ProcurementRequestCreate, ProcurementRequestCreateResponse, ProcurementResultsResponse, ProcurementStatusResponse, ActiveProcurementRequest
from app.services.procurement_service import create_request, get_results, get_status, run_pipeline_for_request
from app.services.region_strategy import get_region_strategy
from app.models.procurement_request import ProcurementRequest
from sqlalchemy import select


router = APIRouter()


@router.post("/request", response_model=ProcurementRequestCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_procurement_request(
    payload: ProcurementRequestCreate,
    background_tasks: BackgroundTasks,
) -> ProcurementRequestCreateResponse:
    try:
        db = SessionLocal()
        try:
            strategy = get_region_strategy(payload.target_country_code)
            print(f"Detected currency: {strategy.default_currency}, Tax rate: {strategy.get_tax_rate()}")
            
            req = create_request(db=db, payload=payload)
            db.commit()
            request_id = req.id
            pipeline_status = req.status
            current_agent = req.current_agent
        finally:
            db.close()
        background_tasks.add_task(run_pipeline_for_request, request_id=request_id, payload=payload)
        return ProcurementRequestCreateResponse(
            request_id=request_id,
            pipeline_status=pipeline_status,
            current_agent=current_agent,
        )
    except Exception as e:
        print("CRITICAL ERROR IN ROUTE:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Backend Crash: {str(e)}")


@router.get("/active", response_model=list[ActiveProcurementRequest])
def get_active_requests() -> list[ActiveProcurementRequest]:
    db = SessionLocal()
    try:
        stmt = select(ProcurementRequest).order_by(ProcurementRequest.created_at.desc()).limit(10)
        requests = db.scalars(stmt).all()
        return [
            ActiveProcurementRequest(
                id=req.id,
                status=req.status,
                material_type=req.material_type,
                quantity=req.quantity,
                unit=req.unit,
                target_country_code=req.target_country_code,
                quality_grade=req.quality_grade,
                created_at=req.created_at
            )
            for req in requests
        ]
    finally:
        db.close()


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


