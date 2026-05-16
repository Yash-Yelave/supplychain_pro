from fastapi import APIRouter

from app.api.routes.procurement import router as procurement_router
from app.api.routes.suppliers import router as suppliers_router

api_router = APIRouter()
api_router.include_router(procurement_router, prefix="/procurement", tags=["procurement"])
api_router.include_router(suppliers_router, prefix="/suppliers", tags=["suppliers"])
