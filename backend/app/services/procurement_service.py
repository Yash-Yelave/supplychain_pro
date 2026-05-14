from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.crud.procurement_requests import create_procurement_request, get_procurement_request, set_request_agent_and_status
from app.models.procurement_request import ProcurementRequest, ProcurementRequestStatus
from app.models.quotation import Quotation
from app.models.report import Report
from app.models.supplier import Supplier
from app.models.trust_score import TrustScore
from app.procurement.pipeline import run_langgraph_from_existing_request, run_sequential_from_existing_request
from app.procurement.state import PipelineStatus, ProcurementRequestInput, ProcurementState
from app.schemas.procurement import (
    ExtractedQuotationRow,
    ProcurementRequestCreate,
    ProcurementResultsResponse,
    ProcurementStatusResponse,
    RankedSupplier,
    TrustScoreRow,
)


def create_request(*, db: Session, payload: ProcurementRequestCreate) -> ProcurementRequest:
    if payload.shipping_deadline < datetime.now(timezone.utc).date():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="deadline must not be in the past",
        )
    req = create_procurement_request(
        db=db,
        material_type=payload.material_type,
        quantity=payload.quantity,
        unit=payload.unit,
        shipping_deadline=payload.shipping_deadline,
        target_country_code=payload.target_country_code,
        quality_grade=payload.quality_grade,
    )
    return req


def run_pipeline_for_request(*, request_id: uuid.UUID, payload: ProcurementRequestCreate) -> None:
    from app.db.context import session_scope

    settings = get_settings()
    with session_scope() as db:
        state = ProcurementState(
            request=ProcurementRequestInput(
                material_type=payload.material_type,
                quantity=payload.quantity,
                unit=payload.unit,
                shipping_deadline=payload.shipping_deadline,
                target_country_code=payload.target_country_code,
                quality_grade=payload.quality_grade,
            ),
            request_id=request_id,
            status=PipelineStatus.discovering,
            active_agent="discovery",
        )
        try:
            if settings.pipeline_use_langgraph:
                run_langgraph_from_existing_request(state, db=db)
            else:
                run_sequential_from_existing_request(state, db=db)
        except Exception as e:
            import traceback
            print(f"Pipeline crashed for request {request_id}:")
            traceback.print_exc()
            set_request_agent_and_status(
                db=db,
                request_id=request_id,
                agent=state.active_agent,
                status=ProcurementRequestStatus.failed,
                completed_at=datetime.now(timezone.utc),
            )
            return


def get_status(*, db: Session, request_id: uuid.UUID) -> ProcurementStatusResponse:
    req = get_procurement_request(db=db, request_id=request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="procurement request not found")

    supplier_count = db.scalar(
        select(func.count()).select_from(Supplier).where(Supplier.material_categories.contains([req.material_type]))
    ) or 0
    quotation_count = db.scalar(select(func.count()).select_from(Quotation).where(Quotation.request_id == request_id)) or 0
    trust_score_count = db.scalar(select(func.count()).select_from(TrustScore).where(TrustScore.request_id == request_id)) or 0

    return ProcurementStatusResponse(
        request_id=req.id,
        pipeline_status=req.status,
        current_agent=req.current_agent,
        supplier_count=int(supplier_count),
        quotation_count=int(quotation_count),
        trust_score_count=int(trust_score_count),
        created_at=req.created_at,
        completed_at=req.completed_at,
    )


def get_results(*, db: Session, request_id: uuid.UUID) -> ProcurementResultsResponse:
    req = db.get(ProcurementRequest, request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="procurement request not found")

    quote_rows = list(
        db.execute(
            select(Quotation, Supplier.name)
            .join(Supplier, Supplier.id == Quotation.supplier_id)
            .where(Quotation.request_id == request_id)
            .order_by(Quotation.created_at)
        ).all()
    )
    trust_rows = list(
        db.execute(
            select(TrustScore, Supplier.name)
            .join(Supplier, Supplier.id == TrustScore.supplier_id)
            .where(TrustScore.request_id == request_id)
            .order_by(TrustScore.composite_score.desc())
        ).all()
    )
    report = db.scalar(select(Report).where(Report.request_id == request_id))

    ranked_suppliers: list[RankedSupplier] = []
    if report is not None:
        ranked_suppliers = [RankedSupplier.model_validate(row) for row in (report.top_suppliers or [])]

    trust_scores = [
        TrustScoreRow(
            supplier_id=ts.supplier_id,
            supplier_name=s_name,
            composite_score=ts.composite_score,
            price_competitiveness=ts.price_competitiveness,
            response_speed_score=ts.response_speed_score,
            quote_completeness=ts.quote_completeness,
            referral_score=ts.referral_score,
            computed_at=ts.computed_at,
        )
        for ts, s_name in trust_rows
    ]

    extracted_quotations = [
        ExtractedQuotationRow(
            quotation_id=q.id,
            supplier_id=q.supplier_id,
            supplier_name=s_name,
            unit_price=q.unit_price,
            currency=q.currency,
            moq=q.moq,
            delivery_days=q.delivery_days,
            validity_days=q.validity_days,
            payment_terms=q.payment_terms,
            notes=q.notes,
            extraction_confidence=q.extraction_confidence,
            missing_fields=list(q.missing_fields or []),
            created_at=q.created_at,
        )
        for q, s_name in quote_rows
    ]

    return ProcurementResultsResponse(
        request_id=req.id,
        pipeline_status=req.status,
        ranked_suppliers=ranked_suppliers,
        trust_scores=trust_scores,
        extracted_quotations=extracted_quotations,
        final_recommendation_report=report.summary_text if report else None,
        analyst_summary=report.summary_text if report else None,
    )
