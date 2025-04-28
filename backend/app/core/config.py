from pydantic import BaseSettings
import os
from pathlib import Path

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    APP_NAME: str = "ModHub Central"
    
    # Database
    DATABASE_URL: str = "sqlite:///./modhub.db"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CONFIG_DIR: Path = BASE_DIR / "config"
    
    # Initialize config directory
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.CONFIG_DIR, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()