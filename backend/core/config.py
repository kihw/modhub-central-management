import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from pydantic_settings import BaseSettings
from pydantic import Field, validator

logger = logging.getLogger(__name__)

class ModHubSettings(BaseSettings):
    HOST: str = Field("127.0.0.1", validation_alias="MODHUB_HOST")
    PORT: int = Field(8668, validation_alias="MODHUB_PORT", ge=1024, le=65535)
    DEBUG: bool = Field(False, validation_alias="MODHUB_DEBUG")
    
    DB_TYPE: str = Field("sqlite", validation_alias="MODHUB_DB_TYPE")
    DB_PATH: str = Field("database.sqlite", validation_alias="MODHUB_DB_PATH")
    DB_HOST: Optional[str] = Field(None, validation_alias="MODHUB_DB_HOST")
    DB_PORT: Optional[int] = Field(None, validation_alias="MODHUB_DB_PORT", ge=1024, le=65535)
    DB_NAME: Optional[str] = Field(None, validation_alias="MODHUB_DB_NAME")
    DB_USER: Optional[str] = Field(None, validation_alias="MODHUB_DB_USER")
    DB_PASSWORD: Optional[str] = Field(None, validation_alias="MODHUB_DB_PASSWORD")
    
    APP_NAME: str = Field("ModHub Central", validation_alias="MODHUB_APP_NAME")
    APP_VERSION: str = Field("0.2.0", validation_alias="MODHUB_APP_VERSION")
    LOG_LEVEL: str = Field("INFO", validation_alias="MODHUB_LOG_LEVEL")
    DATA_DIR: Path = Field(Path.home() / ".modhub", validation_alias="MODHUB_DATA_DIR")
    
    SENTRY_DSN: Optional[str] = Field(None, validation_alias="MODHUB_SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = Field("production", validation_alias="MODHUB_SENTRY_ENVIRONMENT")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(0.1, validation_alias="MODHUB_SENTRY_TRACES_SAMPLE_RATE", ge=0.0, le=1.0)
    SENTRY_PROFILES_SAMPLE_RATE: float = Field(0.1, validation_alias="MODHUB_SENTRY_PROFILES_SAMPLE_RATE", ge=0.0, le=1.0)
    
    AUTO_START_MODS: bool = Field(True, validation_alias="MODHUB_AUTO_START_MODS")
    RULE_CHECK_INTERVAL: float = Field(2.0, validation_alias="MODHUB_RULE_CHECK_INTERVAL", gt=0.1)
    PROCESS_SCAN_INTERVAL: float = Field(5.0, validation_alias="MODHUB_PROCESS_SCAN_INTERVAL", gt=0.1)
    ENABLE_MOD_CONFLICT_RESOLUTION: bool = Field(True, validation_alias="MODHUB_ENABLE_MOD_CONFLICT_RESOLUTION")
    
    ENABLE_CORS: bool = Field(False, validation_alias="MODHUB_ENABLE_CORS")
    CORS_ORIGINS: str = Field("http://localhost:3000", validation_alias="MODHUB_CORS_ORIGINS")
    API_KEY_REQUIRED: bool = Field(True, validation_alias="MODHUB_API_KEY_REQUIRED")
    API_KEY: Optional[str] = Field(None, validation_alias="MODHUB_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v

    @validator("DB_TYPE")
    def validate_db_type(cls, v: str) -> str:
        valid_types = {"sqlite", "postgresql", "mysql"}
        v = v.lower()
        if v not in valid_types:
            raise ValueError(f"Invalid database type. Must be one of {valid_types}")
        return v

    def get_database_url(self) -> str:
        if self.DB_TYPE == "sqlite":
            db_path = self.DATA_DIR / self.DB_PATH
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path.resolve()}"
        
        if self.DB_TYPE in {"postgresql", "mysql"}:
            required_fields = {
                "DB_HOST": self.DB_HOST,
                "DB_PORT": self.DB_PORT,
                "DB_NAME": self.DB_NAME,
                "DB_USER": self.DB_USER,
                "DB_PASSWORD": self.DB_PASSWORD
            }
            missing = [k for k, v in required_fields.items() if v is None]
            if missing:
                raise ValueError(f"Missing required fields for {self.DB_TYPE}: {', '.join(missing)}")
            
            prefix = "mysql+pymysql" if self.DB_TYPE == "mysql" else "postgresql+psycopg2"
            return f"{prefix}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            
    def get_cors_origins(self) -> List[str]:
        if not self.ENABLE_CORS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def get_log_level(self) -> int:
        return getattr(logging, self.LOG_LEVEL)

def load_config_file(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load config file {path}: {e}")
        return {}

settings = ModHubSettings()

config_path = Path(os.getenv("MODHUB_CONFIG_FILE", "config.json")).resolve()
if config_path.exists():
    logger.info(f"Loading configuration from {config_path}")
    file_config = load_config_file(config_path)
    if file_config:
        settings = ModHubSettings(**file_config)