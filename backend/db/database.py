# backend/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Déterminer le chemin de la base de données
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/database.sqlite")

# Créer le répertoire de données s'il n'existe pas
data_dir = BASE_DIR / "data"
data_dir.mkdir(exist_ok=True)

# Créer l'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

# Créer une classe de session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles declaratifs
Base = declarative_base()

# Fonction pour obtenir une instance de DB
def get_db():
    """
    Fournit une session de base de données et assure sa fermeture après utilisation.
    À utiliser comme dépendance dans les routes FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour initialiser les tables dans la base de données
def init_db():
    """
    Initialise le schéma de la base de données.
    À appeler une fois lors du démarrage de l'application.
    """
    from . import models  # Import ici pour éviter les importations circulaires
    Base.metadata.create_all(bind=engine)