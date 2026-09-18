"""
===============================================================================
ROUTEUR CENTRAL DE L'API V1 (ROUTER.PY)
===============================================================================
Rôle :
  Agrège et organise tous les sous-routeurs d'endpoints de l'API version 1 :
  - `/health`    : Point de contrôle de disponibilité et de statut système.
  - `/auth`      : Gestion des comptes, connexions, refresh tokens et OTP.
  - `/audits`    : Gestion des formulaires HSE (création, mise à jour, historique).
  - `/dashboard` : Indicateurs de performance, widgets et graphiques de pilotage.

Équipe de maintenance :
  Ce routeur unifié est monté sur le préfixe global `/api/v1` dans `app/main.py`.
===============================================================================
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, audits, dashboard

# Instance principale du routeur API v1
api_router = APIRouter()

# 1. Endpoint de santé système (sans préfixe additionnel -> /api/v1/health)
api_router.include_router(health.router, tags=["Health Check"])

# 2. Module d'authentification et sécurité (ex: /api/v1/auth/login)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 3. Module des formulaires et audits HSE (ex: /api/v1/audits/)
api_router.include_router(audits.router, prefix="/audits", tags=["Audits HSE"])

# 4. Module du tableau de bord et indicateurs (ex: /api/v1/dashboard/overview)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard & Widgets"])
