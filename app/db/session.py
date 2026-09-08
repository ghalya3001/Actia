import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

# Direct, high-performance PostgreSQL engine connection with automatic pre-ping
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"connect_timeout": 5},
    pool_pre_ping=True,
    pool_recycle=300
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
