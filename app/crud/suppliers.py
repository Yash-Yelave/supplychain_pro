import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.supplier import Supplier


def list_all_suppliers(db: Session | None = None) -> list[Supplier]:
    owns_session = db is None
    db = db or SessionLocal()
    try:
        return list(db.scalars(select(Supplier).order_by(Supplier.name)).all())
    finally:
        if owns_session:
            db.close()


def get_supplier_by_id(supplier_id: uuid.UUID | str, db: Session | None = None) -> Supplier | None:
    owns_session = db is None
    db = db or SessionLocal()
    try:
        return db.get(Supplier, uuid.UUID(str(supplier_id)))
    finally:
        if owns_session:
            db.close()


def get_suppliers_by_category(material_type: str, db: Session | None = None) -> list[Supplier]:
    owns_session = db is None
    db = db or SessionLocal()
    try:
        category = material_type.strip().lower()
        statement = (
            select(Supplier)
            .where(Supplier.material_categories.contains([category]))
            .order_by(Supplier.simulated_response_hours, Supplier.name)
        )
        return list(db.scalars(statement).all())
    finally:
        if owns_session:
            db.close()
