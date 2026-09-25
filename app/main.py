"""
===============================================================================
PLATFORMACTIA - POINT D'ENTRÉE PRINCIPAL FASTAPI (MAIN.PY)
===============================================================================
Rôle :
  Initialise l'application web FastAPI, configure les middlewares (CORS),
  gère le cycle de vie de l'application (création automatique des tables BDD
  et peuplement du catalogue de KPIs), monte les répertoires de fichiers
  statiques (assets compilés Vite) et déclare les routes de l'API REST.

Architecture du cycle de vie :
  - `lifespan(app)` : Fonction asynchrone exécutée au démarrage et à l'arrêt.
    Elle assure la création transparente des tables PostgreSQL sans nécessiter
    de commande manuelle préalable.
  - Montage SPA : Permet de servir directement le frontend construit (`dist/`)
    via la route `/ui` ou en tant qu'application autonome via Uvicorn.

Documentation interactive :
  - Swagger UI : http://localhost:8000/docs
  - ReDoc      : http://localhost:8000/redoc
  - Health API : http://localhost:8000/api/v1/health

Équipe de maintenance :
  Pour lancer le serveur de développement local :
  `uvicorn app.main:app --reload --port 8000`
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


# =============================================================================
# 1. GESTIONNAIRE DE CYCLE DE VIE (LIFESPAN HANDLER)
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie exécuté automatiquement au démarrage et à l'arrêt du serveur HTTP.
    
    Opérations de démarrage :
      1. Importe l'ensemble des modèles SQLAlchemy pour les enregistrer auprès de Base.metadata.
      2. Crée automatiquement toutes les tables ORM dans PostgreSQL (`create_all`).
      3. Initialise le catalogue des définitions de KPIs système si la base est vierge.
    """
    try:
        # Import de tous les modèles pour que Base.metadata en ait la connaissance complète
        import app.models  # noqa: F401

        # Création idempotente des tables (ne recrée pas les tables déjà existantes)
        Base.metadata.create_all(bind=engine)
        print("[DATABASE] OK - Tables PostgreSQL verifiees et pretes.", flush=True)

        # Migration des colonnes RBAC si nécessaire
        from app.db.migrate_rbac import migrate_rbac
        migrate_rbac()

        # Amorçage de l'administrateur par défaut
        from app.db.seed_admin import seed_admin
        seed_admin()

        # Initialisation du catalogue des KPIs par défaut si nécessaire
        from app.services.kpi_service import KPIService
        from app.db.session import SessionLocal
        init_db = SessionLocal()
        try:
            KPIService.ensure_default_kpi_definitions(init_db)
        finally:
            init_db.close()
    except Exception as e:
        print(f"[DATABASE] ERREUR - Creation des tables: {e}", flush=True)

    # Cède le contrôle à l'application en cours d'exécution
    yield
    # Code exécuté lors de l'arrêt gracieux du serveur (aucun nettoyage particulier requis ici)


# =============================================================================
# 2. INITIALISATION ET CONFIGURATION DE L'APPLICATION FASTAPI
# =============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",      # Documentation Swagger UI interactive
    redoc_url="/redoc",    # Documentation ReDoc alternative
    lifespan=lifespan,
)

# Configuration du Middleware CORS (Cross-Origin Resource Sharing)
# Permet au frontend Vue (exécuté sur le port 3000 en dev) de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Autorise toutes les origines en développement
    allow_credentials=True,    # Autorise les cookies et en-têtes d'autorisation
    allow_methods=["*"],        # Autorise toutes les méthodes HTTP (GET, POST, PUT, DELETE...)
    allow_headers=["*"],        # Autorise tous les en-têtes (Authorization, Content-Type...)
)


# =============================================================================
# 3. DISTRIBUTION DES FICHIERS STATIQUES ET INTERFACE WEB SPA
# =============================================================================
# Résolution du chemin absolu racine du projet
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist_dir = os.path.join(base_dir, "dist")
static_dir = os.path.join(base_dir, "static")

# Montage des bundles JS/CSS compilés de l'interface Vue 3
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

# Montage des fichiers statiques d'appoint
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/ui", tags=["Web UI"], include_in_schema=False)
@app.get("/ui/{full_path:path}", tags=["Web UI"], include_in_schema=False)
def serve_ui(full_path: str = ""):
    """
    Sert l'application cliente Single Page Application (SPA) Vue 3.
    Redirige les requêtes de navigation vers le fichier 'index.html' compilé.
    URL d'accès : http://localhost:8000/ui
    """
    dist_index = os.path.join(dist_dir, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    static_index = os.path.join(static_dir, "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {"error": "Fichier d'interface utilisateur introuvable."}


# =============================================================================
# 4. ENREGISTREMENT DES ROUTEURS ET ROUTE RACINE
# =============================================================================
# Inclusion du routeur unifié d'API sous le préfixe '/api/v1'
app.include_router(api_router, prefix=settings.API_V1_STR)

# Alias d'accès direct pour l'administration : /api/admin
from app.api.v1.endpoints import admin as admin_endpoints
app.include_router(admin_endpoints.router, prefix="/api/admin", tags=["Admin User Management (Alias)"])


@app.get("/", tags=["Root"])
def read_root():
    """
    Route d'accueil de base affichant un message de bienvenue et les liens d'accès rapides.
    """
    return {
        "message": f"Bienvenue sur l'API {settings.PROJECT_NAME}",
        "docs": "/docs",
        "ui": "/ui",
        "health": f"{settings.API_V1_STR}/health"
    }
