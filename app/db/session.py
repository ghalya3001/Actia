import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_engine():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql"):
        try:
            # Test PostgreSQL connectivity with a short 2-second timeout
            test_engine = create_engine(db_url, connect_args={"connect_timeout": 2})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL database.")
            return test_engine
        except Exception as err:
            print(f"[Database] PostgreSQL server unavailable ({err}). Falling back to local SQLite: platformactia.db")
            db_url = "sqlite:///./platformactia.db"
    
    engine_kwargs = {}
    if db_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    
    return create_engine(db_url, **engine_kwargs)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
