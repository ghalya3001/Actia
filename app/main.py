"""
===============================================================================
PLATFORMACTIA - POINT D'ENTRÉE PRINCIPAL FASTAPI (MAIN.PY)
===============================================================================
Ce fichier initialise l'application web FastAPI, configure les middlewares
(CORS), monte les fichiers statiques HTML/CSS/JS, crée les tables SQLite/PostgreSQL
et déclare les routes d'API pour le Portail Responsable HSE.

Auteurs / Équipe : CIPI ACTIA - Plateforme HSE
===============================================================================
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine


# -----------------------------------------------------------------------------
# 1. GESTIONNAIRE DE CYCLE DE VIE (LIFESPAN)
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie exécuté au démarrage et à l'arrêt du serveur.
    Initialise automatiquement les tables de base de données ORM SQLAlchemy (SQLite ou PostgreSQL).
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("[DATABASE] Initialisation des tables ORM réussie.")
    except Exception as e:
        print(f"[Warning] Avertissement lors de la création des tables DB : {e}")
    yield


# -----------------------------------------------------------------------------
# 2. INITIALISATION ET CONFIGURATION DE L'APPLICATION FASTAPI
# -----------------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",      # Documentation Swagger UI interactive
    redoc_url="/redoc",    # Documentation ReDoc alternative
    lifespan=lifespan,
)

# Configuration du Middleware CORS pour autoriser l'accès depuis le front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# 3. SERVICE DES FICHIERS STATIQUES ET INTERFACE WEB (FRONTEND)
# -----------------------------------------------------------------------------
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/ui", tags=["Web UI"], include_in_schema=False)
def serve_ui():
    """
    [ROUTE FRONTEND] Servez l'interface utilisateur SPA complète HTML/CSS/JS (index.html).
    Accès navigateur : http://localhost:8000/ui
    """
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "Fichier d'interface utilisateur introuvable."}


# -----------------------------------------------------------------------------
# 4. ENREGISTREMENT DES ROUTES D'API ET ROUTE RACINE
# -----------------------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def read_root():
    """
    [ROUTE RACINE] Message de bienvenue et liens rapides vers les documentations.
    """
    return {
        "message": f"Bienvenue sur l'API {settings.PROJECT_NAME}",
        "docs": "/docs",
        "ui": "/ui",
        "health": f"{settings.API_V1_STR}/health"
    }
