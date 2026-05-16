import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierDirectoryItem

router = APIRouter()


@router.get("/", response_model=list[SupplierDirectoryItem])
def list_suppliers(db: Session = Depends(get_db)):
    """
    Get a list of all suppliers for the directory.
    """
    stmt = select(Supplier).order_by(Supplier.name.asc())
    suppliers = db.scalars(stmt).all()
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierDirectoryItem)
def get_supplier(supplier_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Get a single supplier by ID.
    """
    stmt = select(Supplier).where(Supplier.id == supplier_id)
    supplier = db.scalar(stmt)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier
