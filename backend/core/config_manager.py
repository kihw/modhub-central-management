"""
Advanced Configuration Management Module

Provides comprehensive configuration management with support for
multiple sources, validation, and dynamic updates.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union, Type
from pathlib import Path
import yaml
import toml
import secrets

from pydantic import BaseModel, Field, ValidationError, validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Base exception for configuration-related errors"""
    pass

class ConfigSource(str):
    """Enumeration of supported configuration sources"""
    ENV = 'env'
    FILE = 'file'
    DEFAULT = 'default'
    OVERRIDE = 'override'

class ConfigValidator(BaseModel):
    """
    Base configuration validator with common validation methods
    """
    @validator('*')
    def validate_not_none(cls, v):
        """Ensure no configuration values are None"""
        if v is None:
            raise ValueError("Configuration values cannot be None")
        return v

class ModHubConfiguration(BaseSettings):
    """
    Comprehensive configuration model for ModHub Central
    """
    # Core application settings
    app_name: str = Field(default="ModHub Central", env="MODHUB_APP_NAME")
    version: str = Field(default="0.2.0", env="MODHUB_APP_VERSION")
    environment: str = Field(default="development", env="MODHUB_ENVIRONMENT")
    
    # Server configuration
    host: str = Field(default="0.0.0.0", env="MODHUB_HOST")
    port: int = Field(default=8668, env="MODHUB_PORT")
    debug: bool = Field(default=False, env="MODHUB_DEBUG")
    
    # Logging configuration
    log_level: str = Field(default="INFO", env="MODHUB_LOG_LEVEL")
    log_dir: Path = Field(default_factory=lambda: Path("logs"), env="MODHUB_LOG_DIR")
    
    # Database configuration
    database_url: Optional[str] = Field(default=None, env="MODHUB_DATABASE_URL")
    database_type: str = Field(default="sqlite", env="MODHUB_DATABASE_TYPE")
    
    # Security settings
    secret_key: Optional[str] = Field(default=None, env="MODHUB_SECRET_KEY")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], env="MODHUB_CORS_ORIGINS")
    
    # Plugin system
    plugin_dirs: List[str] = Field(
        default_factory=lambda: [
            str(Path(__file__).parent.parent / "plugins"),
            str(Path.home() / ".modhub" / "plugins")
        ],
        env="MODHUB_PLUGIN_DIRS"
    )
    
    # Performance and resource settings
    process_scan_interval: int = Field(default=5, env="MODHUB_PROCESS_SCAN_INTERVAL")
    resource_monitoring_threshold: Dict[str, float] = Field(
        default_factory=lambda: {
            "cpu": 80.0,
            "memory": 85.0,
            "disk": 90.0
        },
        env="MODHUB_RESOURCE_THRESHOLDS"
    )
    
    # Sentry configuration
    sentry_dsn: Optional[str] = Field(default=None, env="MODHUB_SENTRY_DSN")
    sentry_traces_sample_rate: float = Field(default=0.1, env="MODHUB_SENTRY_TRACES_SAMPLE_RATE")
    
    # Additional validator
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level is a valid option"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v.upper()
    
    # Pydantic configuration
    model_config = ConfigDict(
        env_prefix="MODHUB_",
        case_sensitive=False,
        extra='ignore'
    )

class ConfigurationManager:
    """
    Advanced configuration management with multiple sources and dynamic updates
    """
    
    def __init__(
        self, 
        config_model: Type[BaseSettings] = ModHubConfiguration,
        config_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize configuration manager
        
        Args:
            config_model: Pydantic settings model to use
            config_dir: Optional directory for configuration files
        """
        self._config_model = config_model
        self._config_dir = Path(config_dir or Path.home() / ".modhub")
        
        # Ensure config directory exists
        self._config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration sources tracking
        self._sources: Dict[ConfigSource, Dict[str, Any]] = {
            ConfigSource.DEFAULT: {},
            ConfigSource.ENV: {},
            ConfigSource.FILE: {},
            ConfigSource.OVERRIDE: {}
        }
        
        # Current configuration instance
        self._current_config: Optional[BaseSettings] = None
        
        # Configuration file paths
        self._config_paths = {
            'json': self._config_dir / 'config.json',
            'yaml': self._config_dir / 'config.yaml',
            'toml': self._config_dir / 'config.toml'
        }
    
    def _load_config_file(self, path: Path) -> Dict[str, Any]:
        """
        Load configuration from a specific file
        
        Args:
            path: Path to the configuration file
        
        Returns:
            Parsed configuration dictionary
        """
        if not path.exists():
            return {}
        
        try:
            suffix = path.suffix.lower().lstrip('.')
            
            with open(path, 'r') as f:
                if suffix == 'json':
                    return json.load(f)
                elif suffix in ['yaml', 'yml']:
                    return yaml.safe_load(f)
                elif suffix == 'toml':
                    return toml.load(f)
                else:
                    raise ConfigurationError(f"Unsupported file type: {suffix}")
        
        except (json.JSONDecodeError, yaml.YAMLError, toml.TomlDecodeError) as e:
            logger.error(f"Error parsing config file {path}: {e}")
            return {}
    
    def load_configuration(
        self, 
        env_file: Optional[Union[str, Path]] = None, 
        additional_files: Optional[List[Union[str, Path]]] = None
    ) -> BaseSettings:
        """
        Load configuration from multiple sources
        
        Args:
            env_file: Optional .env file to load environment variables from
            additional_files: Optional list of additional config files to load
        
        Returns:
            Validated configuration instance
        """
        # Load environment variables
        env_config = {}
        
        # Load .env file if specified
        if env_file:
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                logger.warning("python-dotenv not installed. Skipping .env file loading.")
        
        # Try loading from various config file formats
        for path in self._config_paths.values():
            file_config = self._load_config_file(path)
            if file_config:
                self._sources[ConfigSource.FILE].update(file_config)
        
        # Load additional specified config files
        if additional_files:
            for file_path in additional_files:
                file_path = Path(file_path)
                additional_config = self._load_config_file(file_path)
                if additional_config:
                    self._sources[ConfigSource.FILE].update(additional_config)
        
        # Validate and create configuration instance
        try:
            self._current_config = self._config_model()
            
            # Apply configuration from different sources
            # Priority: Override > Environment > File > Default
            sources_priority = [
                ConfigSource.DEFAULT,
                ConfigSource.FILE,
                ConfigSource.ENV,
                ConfigSource.OVERRIDE
            ]
            
            for source in sources_priority:
                source_config = self._sources.get(source, {})
                for key, value in source_config.items():
                    if hasattr(self._current_config, key):
                        setattr(self._current_config, key, value)
            
            return self._current_config
        
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise ConfigurationError("Invalid configuration") from e
    
    def update_configuration(
        self, 
        updates: Dict[str, Any], 
        source: ConfigSource = ConfigSource.OVERRIDE
    ):
        """
        Update configuration dynamically
        
        Args:
            updates: Dictionary of configuration updates
            source: Source of the updates
        """
        # Validate updates against the configuration model
        try:
            # Merge updates with existing configuration
            self._sources[source].update(updates)
            
            # Reload configuration
            self.load_configuration()
            
            logger.info(f"Configuration updated from {source}")
        
        except ValidationError as e:
            logger.error(f"Configuration update validation error: {e}")
            raise ConfigurationError("Invalid configuration update") from e
    
    def generate_secret_key(self) -> str:
        """
        Generate a secure secret key
        
        Returns:
            Randomly generated secret key
        """
        return secrets.token_urlsafe(32)
    
    def save_configuration(self, format: str = 'yaml'):
        """
        Save current configuration to a file
        
        Args:
            format: Configuration file format (json, yaml, toml)
        """
        if not self._current_config:
            raise ConfigurationError("No configuration loaded")
        
        # Select file path based on format
        if format not in self._config_paths:
            raise ConfigurationError(f"Unsupported format: {format}")
        
        config_path = self._config_paths[format]
        
        # Convert configuration to dictionary
        config_dict = self._current_config.model_dump()
        
        try:
            with open(config_path, 'w') as f:
                if format == 'json':
                    json.dump(config_dict, f, indent=2)
                elif format == 'yaml':
                    yaml.safe_dump(config_dict, f, default_flow_style=False)
                elif format == 'toml':
                    toml.dump(config_dict, f)
            
            logger.info(f"Configuration saved to {config_path}")
        
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise ConfigurationError("Failed to save configuration") from e
    
    def get_configuration(self) -> BaseSettings:
        """
        Get the current configuration
        
        Returns:
            Current configuration instance
        """
        if not self._current_config:
            self.load_configuration()
        
        return self._current_config
    
    def reset_configuration(self):
        """
        Reset configuration to default values
        """
        # Clear all sources except default
        for source in [ConfigSource.ENV, ConfigSource.FILE, ConfigSource.OVERRIDE]:
            self._sources[source].clear()
        
        # Reload configuration
        self.load_configuration()
        
        logger.info("Configuration reset to defaults")

# Global configuration manager instance
config_manager = ConfigurationManager()

# Expose key functions and types
__all__ = [
    'ConfigurationManager', 
    'ModHubConfiguration', 
    'ConfigSource', 
    'ConfigurationError',
    'config_manager'
]