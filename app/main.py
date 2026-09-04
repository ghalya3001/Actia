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
# 3. SERVICE DES FICHIERS STATIQUES ET INTERFACE WEB (FRONTEND REACT / STATIC)
# -----------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist_dir = os.path.join(base_dir, "dist")
static_dir = os.path.join(base_dir, "static")

if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/ui", tags=["Web UI"], include_in_schema=False)
@app.get("/ui/{full_path:path}", tags=["Web UI"], include_in_schema=False)
def serve_ui(full_path: str = ""):
    """
    [ROUTE FRONTEND REACT] Servez l'interface utilisateur SPA complète (React Vite dist/index.html).
    Accès navigateur : http://localhost:8000/ui
    """
    dist_index = os.path.join(dist_dir, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    static_index = os.path.join(static_dir, "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
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
