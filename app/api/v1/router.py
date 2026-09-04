from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, audits

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health Check"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(audits.router, prefix="/audits", tags=["Audits HSE"])
