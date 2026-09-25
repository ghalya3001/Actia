"""
===============================================================================
MIGRATION RBAC & CYCLE DE VIE DES COMPTES (MIGRATE_RBAC.PY)
===============================================================================
Rôle :
  Applique les modifications de schéma sur la table 'users' de PostgreSQL :
  - Ajoute la colonne 'role' (défaut 'USER')
  - Ajoute la colonne 'status' (défaut 'PENDING')
  - Ajoute 'rejection_reason', 'reviewed_by', 'reviewed_at'
  - Promeut automatiquement les comptes administrateurs clés (ex: responsable@actia.com)
    avec role = 'ADMIN' et status = 'APPROVED'.
===============================================================================
"""

import sys
import os

# Assure que le répertoire racine du projet est dans sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import text, inspect
from app.db.session import engine


def migrate_rbac():
    print("[MIGRATION RBAC] Début de la mise à niveau du schéma...")
    with engine.begin() as conn:
        # 1. Ajout des colonnes RBAC si elles n'existent pas déjà
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'USER';
        """))
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'PENDING';
        """))
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
        """))
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL;
        """))
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP WITH TIME ZONE;
        """))

        # 2. Création des index pour optimiser les requêtes de filtrage
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_users_role ON users (role);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_users_status ON users (status);
        """))

        # 3. Mise à jour des comptes existants
        # Les comptes managers/admins existants reçoivent le rôle ADMIN et statut APPROVED
        conn.execute(text("""
            UPDATE users 
            SET role = 'ADMIN', status = 'APPROVED'
            WHERE email IN ('responsable@actia.com', 'admin@actia.com', 'test@actia.com', 'hse@actia.com');
        """))
        
        # Pour les autres comptes créés avant la migration, s'assurer qu'ils ont un statut APPROVED
        conn.execute(text("""
            UPDATE users 
            SET status = 'APPROVED'
            WHERE status IS NULL OR status = '';
        """))

    print("[MIGRATION RBAC] Colonnes et index créés avec succès.")

    # 4. Vérification du schéma
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    print(f"[MIGRATION RBAC] Colonnes actuelles de la table 'users' : {columns}")

    with engine.connect() as conn:
        users = conn.execute(text("SELECT id, email, role, status FROM users ORDER BY id;")).fetchall()
        print(f"[MIGRATION RBAC] Liste des utilisateurs ({len(users)}) :")
        for u in users:
            print(f"  - ID {u[0]} | {u[1]} | Role: {u[2]} | Status: {u[3]}")


if __name__ == "__main__":
    migrate_rbac()
