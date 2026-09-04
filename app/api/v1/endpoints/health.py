from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/health", response_model=Dict[str, str], summary="Health check endpoint")
def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "PlatformActia Backend API",
        "version": "1.0.0"
    }
