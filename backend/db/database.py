import os
import logging
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from core.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.get_database_url()
data_dir = Path(settings.DATA_DIR)
data_dir.mkdir(exist_ok=True, parents=True)

engine_config = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "pool_size": settings.DB_POOL_SIZE,
    "max_overflow": settings.DB_MAX_OVERFLOW,
}

if settings.DB_TYPE == "sqlite":
    engine_config["connect_args"] = {"check_same_thread": False}
    
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _):
        with dbapi_connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA foreign_keys=ON")

engine = create_engine(DATABASE_URL, **engine_config)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()

def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()

def init_db() -> None:
    from . import models
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        raise

def cleanup_db() -> None:
    try:
        engine.dispose()
        logger.info("Database connections cleaned up")
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}", exc_info=True)
        raise