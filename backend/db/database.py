import os
import logging
from pathlib import Path
from typing import Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager


from sqlalchemy import create_engine, event, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from core.config import settings

logger = logging.getLogger(__name__)

# Sync database settings
DATABASE_URL = settings.get_database_url()
data_dir = Path(settings.DATA_DIR)
data_dir.mkdir(exist_ok=True, parents=True)

# Async database URL - convert sqlite:/// to sqlite+aiosqlite:///
ASYNC_DATABASE_URL = DATABASE_URL
if DATABASE_URL.startswith('sqlite:///'):
    ASYNC_DATABASE_URL = DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///', 1)
elif DATABASE_URL.startswith('postgresql:'):
    ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql:', 'postgresql+asyncpg:', 1)
elif DATABASE_URL.startswith('mysql:'):
    ASYNC_DATABASE_URL = DATABASE_URL.replace('mysql:', 'mysql+aiomysql:', 1)

# Common engine configuration
engine_config = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

# Add DB pool size if not SQLite
if settings.DB_TYPE != "sqlite":
    engine_config.update({
        "pool_size": getattr(settings, "DB_POOL_SIZE", 5),
        "max_overflow": getattr(settings, "DB_MAX_OVERFLOW", 10),
    })

# SQLite specific configurations
sqlite_config = {}
if settings.DB_TYPE == "sqlite":
    sqlite_config["connect_args"] = {"check_same_thread": False}
    
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _):
        try:
            # Try the regular approach for synchronous connections
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception as e:
            # Log the error but don't crash
            logging.warning(f"Failed to set SQLite pragmas: {e}")

# Create sync and async engines
engine = create_engine(DATABASE_URL, **engine_config, **sqlite_config)
async_engine = create_async_engine(ASYNC_DATABASE_URL, **engine_config)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, autocommit=False, autoflush=False, expire_on_commit=False
)

# Base model for all database models
Base = declarative_base()

# Synchronous context manager
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

# Synchronous generator for FastAPI dependency injection
def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()

# Asynchronous context manager
@asynccontextmanager
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Async database session error: {str(e)}", exc_info=True)
        raise
    finally:
        await session.close()

# Asynchronous generator for FastAPI dependency injection
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Async database connection error: {str(e)}", exc_info=True)
        raise
    finally:
        await session.close()

# Initialize the database tables
def init_db() -> None:
    from . import models
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        raise

# Initialize the database tables asynchronously
async def async_init_db() -> None:
    from . import models
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        raise

# Clean up database connections
def cleanup_db() -> None:
    try:
        engine.dispose()
        logger.info("Database connections cleaned up")
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}", exc_info=True)
        raise

# Clean up async database connections
async def async_cleanup_db() -> None:
    try:
        await async_engine.dispose()
        logger.info("Async database connections cleaned up")
    except Exception as e:
        logger.error(f"Async database cleanup failed: {str(e)}", exc_info=True)
        raise
