from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

class ModState(Enum):
    INACTIVE = auto()
    ACTIVE = auto()
    ERROR = auto()
    PENDING = auto()

class ModPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass(frozen=True)
class ModConfig:
    name: str
    enabled: bool = True
    priority: ModPriority = ModPriority.MEDIUM
    auto_activate: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

class BaseMod:
    def __init__(self, config: ModConfig):
        self._config = config
        self._state = ModState.INACTIVE
        self._last_active: Optional[datetime] = None
        self._error_message: Optional[str] = None
        self._cached_settings: Dict[str, Any] = {}

    @property
    def config(self) -> ModConfig:
        return self._config

    @property
    def state(self) -> ModState:
        return self._state

    @state.setter
    def state(self, value: ModState) -> None:
        if not isinstance(value, ModState):
            raise ValueError("State must be a ModState enum value")
        self._state = value

    async def activate(self) -> bool:
        if not self._config.enabled or self._state == ModState.ACTIVE:
            return False

        self._state = ModState.PENDING
        try:
            if await self._handle_activation():
                self._state = ModState.ACTIVE
                self._last_active = datetime.now(timezone.utc)
                self._error_message = None
                return True
            self._state = ModState.ERROR
            return False
        except Exception as e:
            self._state = ModState.ERROR
            self._error_message = str(e)
            return False

    async def deactivate(self) -> bool:
        if self._state != ModState.ACTIVE:
            return False

        try:
            if await self._handle_deactivation():
                self._state = ModState.INACTIVE
                self._error_message = None
                return True
            self._state = ModState.ERROR
            return False
        except Exception as e:
            self._state = ModState.ERROR
            self._error_message = str(e)
            return False

    async def update_settings(self, settings: Dict[str, Any]) -> bool:
        if not isinstance(settings, dict) or not settings:
            return False

        try:
            self._cached_settings = dict(self._config.settings)
            self._config.settings.update(settings)
            
            if self._state == ModState.ACTIVE and not await self._apply_settings():
                self._config.settings = self._cached_settings.copy()
                return False
            return True
        except Exception as e:
            self._error_message = str(e)
            if self._cached_settings:
                self._config.settings = self._cached_settings.copy()
            return False

    async def get_status(self) -> Dict[str, Any]:
        return {
            "name": self._config.name,
            "state": self._state.name,
            "enabled": self._config.enabled,
            "priority": self._config.priority.name,
            "last_active": self._last_active.isoformat() if self._last_active else None,
            "error": self._error_message,
            "settings": dict(self._config.settings)
        }

    async def _handle_activation(self) -> bool:
        raise NotImplementedError

    async def _handle_deactivation(self) -> bool:
        raise NotImplementedError

    async def _apply_settings(self) -> bool:
        raise NotImplementedError

    def __lt__(self, other: 'BaseMod') -> bool:
        if not isinstance(other, BaseMod):
            return NotImplemented
        return self._config.priority.value < other._config.priority.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseMod):
            return NotImplemented
        return self._config.name == other._config.name

    def __hash__(self) -> int:
        return hash(self._config.name)