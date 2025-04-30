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
    pass

class ConfigSource:
    ENV = 'env'
    FILE = 'file'
    DEFAULT = 'default'
    OVERRIDE = 'override'

class ModHubConfiguration(BaseSettings):
    app_name: str = Field(default="ModHub Central", env="MODHUB_APP_NAME")
    version: str = Field(default="0.2.0", env="MODHUB_APP_VERSION")
    environment: str = Field(default="development", env="MODHUB_ENVIRONMENT")
    host: str = Field(default="127.0.0.1", env="MODHUB_HOST")
    port: int = Field(default=8668, ge=1024, le=65535, env="MODHUB_PORT")
    debug: bool = Field(default=False, env="MODHUB_DEBUG")
    log_level: str = Field(default="INFO", env="MODHUB_LOG_LEVEL")
    log_dir: Path = Field(default=Path("logs"), env="MODHUB_LOG_DIR")
    database_url: Optional[str] = Field(default=None, env="MODHUB_DATABASE_URL")
    database_type: str = Field(default="sqlite", env="MODHUB_DATABASE_TYPE")
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="MODHUB_SECRET_KEY")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="MODHUB_CORS_ORIGINS")
    plugin_dirs: List[Path] = Field(
        default=[
            Path(__file__).parent.parent / "plugins",
            Path.home() / ".modhub" / "plugins"
        ],
        env="MODHUB_PLUGIN_DIRS"
    )
    process_scan_interval: int = Field(default=5, ge=1, le=60, env="MODHUB_PROCESS_SCAN_INTERVAL")
    resource_monitoring_threshold: Dict[str, float] = Field(
        default={
            "cpu": 80.0,
            "memory": 85.0,
            "disk": 90.0
        }
    )
    sentry_dsn: Optional[str] = Field(default=None, env="MODHUB_SENTRY_DSN")
    sentry_traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0, env="MODHUB_SENTRY_TRACES_SAMPLE_RATE")

    @validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v

    @validator('resource_monitoring_threshold')
    def validate_thresholds(cls, v: Dict[str, float]) -> Dict[str, float]:
        for key, value in v.items():
            if not 0.0 <= value <= 100.0:
                raise ValueError(f"Threshold {key} must be between 0 and 100")
        return v

    model_config = ConfigDict(
        env_prefix="MODHUB_",
        case_sensitive=False,
        validate_assignment=True
    )

class ConfigurationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        config_model: Type[BaseSettings] = ModHubConfiguration,
        config_dir: Optional[Union[str, Path]] = None
    ):
        if not hasattr(self, '_initialized'):
            self._config_model = config_model
            self._config_dir = Path(config_dir or Path.home() / ".modhub").resolve()
            self._config_dir.mkdir(parents=True, exist_ok=True)
            self._sources = {source: {} for source in [ConfigSource.ENV, ConfigSource.FILE, 
                                                     ConfigSource.DEFAULT, ConfigSource.OVERRIDE]}
            self._current_config = None
            self._config_paths = {
                'json': self._config_dir / 'config.json',
                'yaml': self._config_dir / 'config.yaml',
                'toml': self._config_dir / 'config.toml'
            }
            self._initialized = True

    def _load_config_file(self, path: Path) -> Dict[str, Any]:
        if not path.exists() or not path.is_file():
            return {}
        
        loaders = {
            'json': json.load,
            'yaml': yaml.safe_load,
            'yml': yaml.safe_load,
            'toml': toml.load
        }
        
        suffix = path.suffix.lower().lstrip('.')
        if suffix not in loaders:
            raise ConfigurationError(f"Unsupported file type: {suffix}")
            
        try:
            with path.open('r', encoding='utf-8') as f:
                return loaders[suffix](f)
        except Exception as e:
            logger.error(f"Error loading config file {path}: {str(e)}")
            return {}

    def load_configuration(
        self,
        env_file: Optional[Union[str, Path]] = None,
        additional_files: Optional[List[Union[str, Path]]] = None
    ) -> BaseSettings:
        try:
            if env_file:
                env_path = Path(env_file).resolve()
                if env_path.exists():
                    try:
                        from dotenv import load_dotenv
                        load_dotenv(env_path)
                    except ImportError:
                        logger.warning("python-dotenv not installed, skipping env file")

            config_data = {}
            for path in self._config_paths.values():
                config_data.update(self._load_config_file(path))
            self._sources[ConfigSource.FILE].update(config_data)

            if additional_files:
                for file_path in map(lambda f: Path(f).resolve(), additional_files):
                    self._sources[ConfigSource.FILE].update(self._load_config_file(file_path))

            final_config = {}
            for source in (ConfigSource.DEFAULT, ConfigSource.FILE, ConfigSource.ENV, ConfigSource.OVERRIDE):
                final_config.update(self._sources.get(source, {}))
            
            self._current_config = self._config_model(**final_config)
            return self._current_config
        except Exception as e:
            raise ConfigurationError(f"Configuration loading failed: {str(e)}")

    def update_configuration(self, updates: Dict[str, Any], source: str = ConfigSource.OVERRIDE) -> None:
        if source not in self._sources:
            raise ConfigurationError(f"Invalid configuration source: {source}")
            
        self._sources[source].update(updates)
        self.load_configuration()

    def save_configuration(self, format: str = 'yaml') -> None:
        if not self._current_config:
            raise ConfigurationError("No configuration loaded")
        if format not in self._config_paths:
            raise ConfigurationError(f"Unsupported format: {format}")

        config_path = self._config_paths[format]
        config_dict = self._current_config.model_dump(exclude_none=True)

        dumpers = {
            'json': lambda f: json.dump(config_dict, f, indent=2),
            'yaml': lambda f: yaml.safe_dump(config_dict, f, default_flow_style=False),
            'toml': lambda f: toml.dump(config_dict, f)
        }

        try:
            with config_path.open('w', encoding='utf-8') as f:
                dumpers[format](f)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")

    def get_configuration(self) -> BaseSettings:
        if not self._current_config:
            self.load_configuration()
        return self._current_config

    def reset_configuration(self) -> None:
        self._sources = {source: {} for source in [ConfigSource.ENV, ConfigSource.FILE,
                                                 ConfigSource.DEFAULT, ConfigSource.OVERRIDE]}
        self.load_configuration()

config_manager = ConfigurationManager()

__all__ = ['ConfigurationManager', 'ModHubConfiguration', 'ConfigSource', 'ConfigurationError', 'config_manager']