"""
===============================================================================
GESTION DES CONNEXIONS ET SESSIONS SQLALCHEMY (SESSION.PY)
===============================================================================
Rôle :
  Configure le moteur de connexion (Engine) à la base de données PostgreSQL
  et la fabrique de sessions transactionnelles (`SessionLocal`).

Caractéristiques de performance et résilience :
  - `connect_timeout=5` : Évite les blocages indéfinis si la base est inaccessible.
  - `pool_pre_ping=True` : Teste la validité de la connexion avant chaque requête
    (détecte les connexions interrompues ou les redémarrages de PostgreSQL).
  - `pool_recycle=300` : Recycle les connexions toutes les 5 minutes pour prévenir
    les déconnexions silencieuses imposées par les pare-feu ou le serveur.

Équipe de maintenance :
  Dans les endpoints FastAPI, n'utilisez pas `SessionLocal()` directement ;
  injectez plutôt la dépendance standard `db: Session = Depends(get_db)`
  déclarée dans `app/api/deps.py`.
===============================================================================
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- 1. Moteur SQLAlchemy connecté à PostgreSQL ---
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"connect_timeout": 5},  # Timeout de tentative de connexion à 5 secondes
    pool_pre_ping=True,                  # Teste systématiquement la connexion (SELECT 1)
    pool_recycle=300                     # Renouvelle les connexions inactives après 300 secondes
)

# --- 2. Usine de sessions transactionnelles (SessionLocal) ---
# autocommit=False : les modifications nécessitent un db.commit() explicite
# autoflush=False  : évite d'envoyer prématurément des requêtes avant validation
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
