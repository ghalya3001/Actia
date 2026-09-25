"""
===============================================================================
SCRIPT D'AMORÇAGE DE L'ADMINISTRATEUR (SEED_ADMIN.PY)
===============================================================================
Rôle :
  Initialise ou met à jour de façon idempotente le premier compte administrateur :
  - Lit 'ADMIN_EMAIL' et 'ADMIN_PASSWORD' depuis les variables d'environnement.
  - Valeurs de repli sécurisées pour le développement local.
  - Crée le compte s'il n'existe pas ou le promeut avec role = 'ADMIN' et status = 'APPROVED'.
===============================================================================
"""

import sys
import os

# Assure que le répertoire racine du projet est dans sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password, verify_password
from app.core.config import settings


def seed_admin(db: Session = None) -> User:
    """
    Crée ou synchronise l'administrateur principal dans la base de données
    à partir des variables définies dans app/core/config.py et le fichier .env.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        admin_email = settings.ADMIN_EMAIL.strip().lower()
        admin_password = settings.ADMIN_PASSWORD.strip()
        admin_name = settings.ADMIN_NAME.strip()

        user = db.query(User).filter(User.email == admin_email).first()

        if user:
            # L'utilisateur existe déjà : on s'assure qu'il est ADMIN et APPROVED
            user.role = UserRole.ADMIN.value
            user.status = UserStatus.APPROVED.value
            user.is_active = True
            user.full_name = admin_name

            # Si le mot de passe dans .env ou config a été modifié, on le synchronise automatiquement
            if not user.hashed_password or not verify_password(admin_password, user.hashed_password):
                user.hashed_password = hash_password(admin_password)
                print(f"[SEED ADMIN] Mot de passe administrateur synchronisé depuis .env pour {admin_email}.")
            db.commit()
            db.refresh(user)
            print(f"[SEED ADMIN] Compte administrateur {admin_email} vérifié (Role: ADMIN, Status: APPROVED).")
            return user
        else:
            # Création du premier compte administrateur à partir de la configuration .env
            new_admin = User(
                email=admin_email,
                full_name=admin_name,
                hashed_password=hash_password(admin_password),
                role=UserRole.ADMIN.value,
                status=UserStatus.APPROVED.value,
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            print(f"[SEED ADMIN] Nouvel administrateur créé depuis .env : {admin_email} (Role: ADMIN, Status: APPROVED).")
            return new_admin

    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_admin()
