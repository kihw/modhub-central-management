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
# In backend/db/database.py, improve the init_db function:

# Amélioration dans backend/db/database.py

def init_db() -> None:
    from . import models
    try:
        # S'assurer que le répertoire de données existe
        data_dir = Path(settings.DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Enregistrer tous les modèles explicitement avant la création des tables
        # Cela aide à résoudre les problèmes de dépendances circulaires
        from .models import Base, Mod, User, UserSettings, AutomationRule, Condition, Action, Log
        from .models import Process, DeviceState, Variable, Setting, ActionLog
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        
        # Vérifier la création en essayant d'accéder à une table clé
        with db_session() as session:
            try:
                # Vérifier si la table mods existe
                first_mod = session.query(Mod).first()
                logger.info(f"Mod table verified: {'data found' if first_mod else 'no data yet'}")
                
                # Vérifier également d'autres tables essentielles
                first_user = session.query(User).first()
                logger.info(f"User table verified: {'data found' if first_user else 'no data yet'}")
                
                first_rule = session.query(AutomationRule).first()
                logger.info(f"AutomationRule table verified: {'data found' if first_rule else 'no data yet'}")
                
                # Si aucun utilisateur n'existe, créer un utilisateur système par défaut
                if not first_user:
                    from hashlib import sha256
                    import secrets
                    
                    # Générer un mot de passe sécurisé
                    temp_password = secrets.token_urlsafe(12)
                    hashed_password = sha256(temp_password.encode()).hexdigest()
                    
                    system_user = User(
                        username="system",
                        email="system@modhub.local",
                        hashed_password=hashed_password,
                        is_admin=True
                    )
                    session.add(system_user)
                    session.commit()
                    
                    # Créer les paramètres utilisateur par défaut
                    user_settings = UserSettings(
                        user_id=system_user.id,
                        theme="dark",
                        notifications_enabled=True,
                        auto_backup=True,
                        preferences={}
                    )
                    session.add(user_settings)
                    session.commit()
                    
                    logger.info(f"Created default system user with temporary password: {temp_password}")
                    logger.info("IMPORTANT: Please change this password immediately after first login!")
                
            except Exception as table_error:
                logger.error(f"Error verifying tables: {str(table_error)}")
                raise
                
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        
        # Essayer de créer les tables une par une pour identifier les problèmes spécifiques
        try:
            with engine.begin() as conn:
                # Récupérer tous les objets de table de Base.metadata
                for table in Base.metadata.sorted_tables:
                    try:
                        if not engine.dialect.has_table(conn, table.name):
                            table.create(bind=conn)
                            logger.info(f"Table {table.name} created successfully")
                        else:
                            logger.info(f"Table {table.name} already exists")
                    except Exception as table_error:
                        logger.error(f"Failed to create table {table.name}: {str(table_error)}")
        except Exception as recovery_error:
            logger.error(f"Recovery attempt failed: {str(recovery_error)}")
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

def manual_db_init():
    from db.models import Base
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Manual database initialization completed successfully")
    except Exception as e:
        logger.error(f"Manual database initialization failed: {str(e)}", exc_info=True)
        raise