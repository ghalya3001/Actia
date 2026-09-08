"""
Script de diagnostic de la base de données PostgreSQL.
Vérifie la connexion, crée la base si nécessaire, et crée toutes les tables ORM.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== Diagnostic PlatformActia PostgreSQL ===\n")

# Step 1: Test basic PostgreSQL connection
print("1. Test connexion PostgreSQL (postgres/postgres sur 127.0.0.1:5432)...")
try:
    import psycopg
    conn = psycopg.connect(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
        autocommit=True
    )
    print("   ✅ Connexion PostgreSQL réussie!")

    # Check if platformactia_db exists
    cur = conn.execute("SELECT datname FROM pg_database WHERE datname = 'platformactia_db'")
    rows = cur.fetchall()
    if rows:
        print("   ✅ La base de données 'platformactia_db' existe déjà.")
    else:
        conn.execute("CREATE DATABASE platformactia_db")
        print("   ✅ La base de données 'platformactia_db' a été créée avec succès!")
    conn.close()
except Exception as e:
    print(f"   ❌ ERREUR connexion PostgreSQL: {e}")
    print("   --> Vérifiez que PostgreSQL est démarré et que le mot de passe est 'postgres'")
    sys.exit(1)

# Step 2: Test app DATABASE_URL
print("\n2. Test connexion via SQLAlchemy (DATABASE_URL)...")
try:
    from app.core.config import settings
    print(f"   DATABASE_URL = {settings.DATABASE_URL}")
    from sqlalchemy import create_engine, text
    engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 5})
    with engine.connect() as con:
        result = con.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   ✅ SQLAlchemy connecté! PostgreSQL: {version[:50]}...")
except Exception as e:
    print(f"   ❌ ERREUR SQLAlchemy: {e}")
    sys.exit(1)

# Step 3: Create all ORM tables
print("\n3. Création des tables ORM...")
try:
    from app.db.base import Base
    from app.db.session import engine
    import app.models.user  # Import models to register them
    Base.metadata.create_all(bind=engine)
    print("   ✅ Toutes les tables ORM créées avec succès!")
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"   Tables créées: {', '.join(tables)}")
except Exception as e:
    print(f"   ❌ ERREUR création des tables: {e}")
    sys.exit(1)

# Step 4: Count existing users
print("\n4. Vérification des utilisateurs existants...")
try:
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    from app.models.user import User
    count = db.query(User).count()
    users = db.query(User).all()
    print(f"   Nombre d'utilisateurs dans la base: {count}")
    for u in users:
        print(f"   - {u.email} (is_active={u.is_active})")
    db.close()
except Exception as e:
    print(f"   ❌ ERREUR lecture utilisateurs: {e}")

print("\n=== Diagnostic terminé avec succès! ===")
print("Vous pouvez lancer le serveur: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
