from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
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
