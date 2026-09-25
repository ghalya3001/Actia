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
from app.core.security import hash_password


def seed_admin(db: Session = None) -> User:
    """
    Crée ou promeut l'administrateur par défaut dans la base de données.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@actia.com").strip().lower()
        # Mot de passe par défaut pour le développement local si non configuré en env
        admin_password = os.getenv("ADMIN_PASSWORD", "AdminSecure2026!").strip()
        admin_name = os.getenv("ADMIN_NAME", "Administrateur HSE Actia").strip()

        user = db.query(User).filter(User.email == admin_email).first()

        if user:
            # L'utilisateur existe déjà : on s'assure qu'il est ADMIN et APPROVED
            user.role = UserRole.ADMIN.value
            user.status = UserStatus.APPROVED.value
            user.is_active = True
            # On ne réinitialise PAS le mot de passe s'il existe déjà, sauf si demandé via FORCE_RESET_ADMIN_PASSWORD
            if not user.hashed_password or os.getenv("FORCE_RESET_ADMIN_PASSWORD", "false").lower() == "true":
                user.hashed_password = hash_password(admin_password)
                print(f"[SEED ADMIN] Mot de passe administrateur {admin_email} réinitialisé par configuration.")
            db.commit()
            db.refresh(user)
            print(f"[SEED ADMIN] Compte administrateur {admin_email} vérifié (Role: ADMIN, Status: APPROVED).")
            return user
        else:
            # Création du premier compte administrateur
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
            print(f"[SEED ADMIN] Nouvel administrateur créé : {admin_email} (Role: ADMIN, Status: APPROVED).")
            return new_admin

    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_admin()
