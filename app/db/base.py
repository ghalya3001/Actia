"""
===============================================================================
CLASSE DE BASE DÉCLARATIVE SQLALCHEMY (BASE.PY)
===============================================================================
Rôle :
  Initialise la classe `Base` de l'ORM SQLAlchemy (declarative_base).
  Tous les modèles de données de l'application (User, FormSubmission, etc.)
  héritent de cette classe afin d'être enregistrés dans le catalogue de métadonnées
  et automatiquement créés dans la base de données PostgreSQL.

Équipe de maintenance :
  - `Base.metadata` contient le registre global de toutes les tables ORM.
  - C'est ce catalogue qui est exécuté par `Base.metadata.create_all(bind=engine)`
    dans le fichier `app/main.py` lors du démarrage de l'application.
===============================================================================
"""

from sqlalchemy.orm import declarative_base

# Instance maîtresse de base déclarative pour tous les modèles ORM SQLAlchemy
Base = declarative_base()
