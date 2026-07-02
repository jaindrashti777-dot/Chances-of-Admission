from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.get_database_url,
    pool_pre_ping=True,
    pool_size=settings.SQLACHEMY_POOL_SIZE,
    max_overflow=settings.SQLACHEMY_MAX_OVERFLOW,
    **( {"connect_args": {"check_same_thread": False}} if settings.get_database_url.startswith("sqlite") else {} )
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that provides a database session and ensures it's closed.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
