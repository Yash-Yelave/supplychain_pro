from fastapi import APIRouter

from app.api.routes.procurement import router as procurement_router


api_router = APIRouter()
api_router.include_router(procurement_router, prefix="/procurement", tags=["procurement"])
