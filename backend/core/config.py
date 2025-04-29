"""
Configuration module for ModHub Central.
Handles loading and accessing configuration settings from environment 
variables and configuration files.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Importation depuis pydantic-settings au lieu de pydantic
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)

class ModHubSettings(BaseSettings):
    """
    Application settings with defaults and environment variable support.
    
    Settings can be overridden by environment variables with the prefix MODHUB_,
    e.g., MODHUB_HOST, MODHUB_PORT, etc.
    """
    # API Server settings
    HOST: str = Field("0.0.0.0", validation_alias="MODHUB_HOST")
    PORT: int = Field(8668, validation_alias="MODHUB_PORT")
    DEBUG: bool = Field(False, validation_alias="MODHUB_DEBUG")
    
    # Database settings
    DB_TYPE: str = Field("sqlite", validation_alias="MODHUB_DB_TYPE")
    DB_PATH: str = Field("../data/database.sqlite", validation_alias="MODHUB_DB_PATH")
    DB_HOST: Optional[str] = Field(None, validation_alias="MODHUB_DB_HOST")
    DB_PORT: Optional[int] = Field(None, validation_alias="MODHUB_DB_PORT")
    DB_NAME: Optional[str] = Field(None, validation_alias="MODHUB_DB_NAME")
    DB_USER: Optional[str] = Field(None, validation_alias="MODHUB_DB_USER")
    DB_PASSWORD: Optional[str] = Field(None, validation_alias="MODHUB_DB_PASSWORD")
    
    # Application settings
    APP_NAME: str = Field("ModHub Central", validation_alias="MODHUB_APP_NAME")
    APP_VERSION: str = Field("0.1.0", validation_alias="MODHUB_APP_VERSION")
    LOG_LEVEL: str = Field("INFO", validation_alias="MODHUB_LOG_LEVEL")
    DATA_DIR: str = Field("../data", validation_alias="MODHUB_DATA_DIR")
    
    # Behavior settings
    AUTO_START_MODS: bool = Field(True, validation_alias="MODHUB_AUTO_START_MODS")
    RULE_CHECK_INTERVAL: float = Field(2.0, validation_alias="MODHUB_RULE_CHECK_INTERVAL")
    PROCESS_SCAN_INTERVAL: float = Field(5.0, validation_alias="MODHUB_PROCESS_SCAN_INTERVAL")
    ENABLE_MOD_CONFLICT_RESOLUTION: bool = Field(True, validation_alias="MODHUB_ENABLE_MOD_CONFLICT_RESOLUTION")
    
    # Security settings
    ENABLE_CORS: bool = Field(True, validation_alias="MODHUB_ENABLE_CORS")
    CORS_ORIGINS: str = Field("*", validation_alias="MODHUB_CORS_ORIGINS")
    API_KEY_REQUIRED: bool = Field(False, validation_alias="MODHUB_API_KEY_REQUIRED")
    API_KEY: Optional[str] = Field(None, validation_alias="MODHUB_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_database_url(self) -> str:
        """
        Get the database URL based on configuration.
        
        Returns:
            Database connection URL
        """
        if self.DB_TYPE == "sqlite":
            # Ensure data directory exists
            db_path = Path(self.DB_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"
        elif self.DB_TYPE == "postgresql":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_TYPE == "mysql":
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            raise ValueError(f"Unsupported database type: {self.DB_TYPE}")
            
    def get_cors_origins(self) -> List[str]:
        """
        Get CORS origins as a list.
        
        Returns:
            List of allowed origins
        """
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return self.CORS_ORIGINS.split(",")

    def get_log_level(self) -> int:
        """
        Get the logging level as an integer.
        
        Returns:
            Logging level
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(self.LOG_LEVEL.upper(), logging.INFO)


def load_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}")
            return {}
            
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        return {}


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries, with override_config taking precedence.
    
    Args:
        base_config: Base configuration
        override_config: Configuration that overrides base values
        
    Returns:
        Merged configuration
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_configs(result[key], value)
        else:
            # Override or add the value
            result[key] = value
            
    return result


# Create the settings instance
settings = ModHubSettings()

# Apply additional configuration from file if needed
config_path = os.environ.get("MODHUB_CONFIG_FILE", "config.json")
if Path(config_path).exists():
    logger.info(f"Loading configuration from {config_path}")
    file_config = load_config_file(config_path)
    
    # Update settings from file config
    for key, value in file_config.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
