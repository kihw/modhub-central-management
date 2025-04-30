from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Any, Optional
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime


class ModState(Enum):
    INACTIVE = auto()
    ACTIVE = auto()
    ERROR = auto()
    PAUSED = auto()
    INITIALIZING = auto()


@dataclass
class ModMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: Optional[str] = None
    version: str = "0.1.0"
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activated: Optional[datetime] = None
    total_activation_time: int = 0
    activation_count: int = 0


class ModBase(ABC):
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        priority: int = 50
    ) -> None:
        self._metadata = ModMetadata(
            name=name,
            description=description
        )
        self._state = ModState.INACTIVE
        self._priority = max(0, min(100, priority))
        self._logger = logging.getLogger(f"mod.{name.lower()}")
        self._config: Dict[str, Any] = {}
        self._activation_start: Optional[datetime] = None

    @property
    def metadata(self) -> ModMetadata:
        return self._metadata

    @property
    def state(self) -> ModState:
        return self._state

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def config(self) -> Dict[str, Any]:
        return self._config.copy()

    def update_config(self, config: Dict[str, Any]) -> None:
        if not isinstance(config, dict):
            raise TypeError("Configuration must be a dictionary")
        if not self.validate_config(config):
            raise ValueError("Invalid configuration")
        self._config.update(config)
        self._logger.info(f"Configuration updated: {config}")

    @abstractmethod
    def activate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        pass

    def _update_activation_metrics(self, success: bool) -> None:
        current_time = datetime.now()
        if success and self._state == ModState.ACTIVE:
            self._metadata.activation_count += 1
            self._metadata.last_activated = current_time
            if self._activation_start:
                duration = int((current_time - self._activation_start).total_seconds())
                self._metadata.total_activation_time += duration
            self._activation_start = current_time
        else:
            self._activation_start = None

    def _log_state_change(self, old_state: ModState, new_state: ModState) -> None:
        if old_state != new_state:
            self._logger.info(f"State changed from {old_state.name} to {new_state.name}")
            self._state = new_state

    def validate_config(self, config: Dict[str, Any]) -> bool:
        try:
            return bool(config)
        except Exception as e:
            self._logger.error(f"Config validation failed: {e}")
            return False