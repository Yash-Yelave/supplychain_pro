from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.procurement_request import ProcurementRequest, ProcurementRequestStatus


def create_procurement_request(
    *,
    db: Session,
    material_type: str,
    quantity: float,
    unit: str,
    shipping_deadline: date,
    target_country_code: str,
    quality_grade: str,
) -> ProcurementRequest:
    req = ProcurementRequest(
        material_type=material_type.strip().lower(),
        quantity=quantity,
        unit=unit.strip(),
        shipping_deadline=shipping_deadline,
        target_country_code=target_country_code,
        quality_grade=quality_grade,
        status=ProcurementRequestStatus.in_progress,
        current_agent="supervisor",
    )
    db.add(req)
    db.flush()
    return req


def set_request_agent_and_status(
    *,
    db: Session,
    request_id: uuid.UUID,
    agent: str | None,
    status: ProcurementRequestStatus | str | None = None,
    completed_at: datetime | None = None,
) -> None:
    req = db.get(ProcurementRequest, request_id)
    if req is None:
        raise RuntimeError(f"ProcurementRequest not found: {request_id}")
    req.current_agent = agent
    if status is not None:
        req.status = ProcurementRequestStatus(status)
    if completed_at is not None:
        req.completed_at = completed_at
    db.flush()


def get_procurement_request(*, db: Session, request_id: uuid.UUID) -> ProcurementRequest | None:
    return db.get(ProcurementRequest, request_id)


def list_requests_by_material(*, db: Session, material_type: str) -> list[ProcurementRequest]:
    stmt = select(ProcurementRequest).where(ProcurementRequest.material_type == material_type.strip().lower())
    return list(db.scalars(stmt).all())

