"""
===============================================================================
ENDPOINT DE CONTRÔLE DE SANTÉ DU SYSTÈME (HEALTH.PY)
===============================================================================
Rôle :
  Expose la route `/api/v1/health` permettant aux sondes d'infrastructure
  (load balancers, Docker, Kubernetes, Uptime monitors) de vérifier que le
  serveur FastAPI est en ligne et répond convenablement.
===============================================================================
"""

from fastapi import APIRouter
from typing import Dict

router = APIRouter()


@router.get("/health", response_model=Dict[str, str], summary="Point de contrôle de santé du serveur (Health Check)")
def health_check() -> Dict[str, str]:
    """
    Retourne l'état opérationnel actuel de l'API Backend.

    Returns:
        Dict[str, str]: Objet JSON avec le statut 'ok', le nom du service et la version.
    """
    return {
        "status": "ok",
        "service": "PlatformActia Backend API",
        "version": "1.0.0"
    }
