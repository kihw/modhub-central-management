"""
Database configuration and session management for ModHub Central.
This module sets up the database connection, ORM, and session handling.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from core.config import settings

logger = logging.getLogger(__name__)

# Get database URL from settings
DATABASE_URL = settings.get_database_url()

# Ensure data directory exists
data_dir = Path(settings.DATA_DIR)
data_dir.mkdir(exist_ok=True, parents=True)

logger.info(f"Using database: {DATABASE_URL}")

# Create SQLAlchemy engine with appropriate options
if settings.DB_TYPE == "sqlite":
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},  # Required for SQLite
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=3600,   # Reconnect after 1 hour of idle
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Function to get database session
def get_db():
    """
    Provide a database session and ensure its closure.
    Usage as a FastAPI dependency in routes.
    
    Yields:
        SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database schema
def init_db():
    """
    Initialize database schema.
    Call this once during application startup.
    """
    from . import models  # Import here to avoid circular imports
    
    logger.info("Creating database tables if they don't exist")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Database initialized")
