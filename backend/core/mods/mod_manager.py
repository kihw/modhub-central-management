import logging
from typing import Dict, Any, List, Optional
import threading
from dataclasses import dataclass, field
from enum import Enum, auto

from .mod_base import ModBase
from .gaming_mod import GamingMod
from .media_mod import MediaMod
from .night_mod import NightMod

logger = logging.getLogger(__name__)

class ModStatus(Enum):
    INACTIVE = auto()
    ACTIVE = auto()
    ERROR = auto()

@dataclass
class ModState:
    status: ModStatus = ModStatus.INACTIVE
    instance: ModBase = field(default=None)
    config: Dict[str, Any] = field(default_factory=dict)

class ModManager:
    def __init__(self):
        self._mods: Dict[str, ModState] = {}
        self._active_mods: Dict[str, ModBase] = {}
        self._mod_lock = threading.RLock()
        self._initialize_default_mods()

    def _initialize_default_mods(self) -> None:
        default_mods = {
            "gaming": GamingMod(),
            "night": NightMod(),
            "media": MediaMod()
        }
        
        for mod_id, mod_instance in default_mods.items():
            if not self.register_mod(mod_id, mod_instance):
                logger.error(f"Failed to register default mod: {mod_id}")
                raise RuntimeError(f"Failed to register default mod: {mod_id}")

    def register_mod(self, mod_id: str, mod_instance: ModBase) -> bool:
        if not isinstance(mod_instance, ModBase) or not mod_id:
            return False
            
        with self._mod_lock:
            if mod_id in self._mods:
                return False
                
            self._mods[mod_id] = ModState(instance=mod_instance)
            return True

    def unregister_mod(self, mod_id: str) -> bool:
        with self._mod_lock:
            if mod_id not in self._mods:
                return False
                
            if self.is_mod_active(mod_id):
                self.deactivate_mod(mod_id)
                    
            del self._mods[mod_id]
            return True

    
    # In backend/core/mods/mod_manager.py, modify the activate_mod method
    def activate_mod(self, mod_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        with self._mod_lock:
            mod_state = self._mods.get(mod_id)
            if not mod_state or mod_state.status == ModStatus.ACTIVE:
                return False
    
            try:
                # Handle mod_id that might be a type name
                if mod_id not in self._mods and mod_id in ["gaming", "night", "media", "custom"]:
                    # Try to find mod by type instead of id
                    for id, state in self._mods.items():
                        if hasattr(state.instance, 'type') and state.instance.type == mod_id:
                            mod_id = id
                            mod_state = state
                            break
                        
                if not mod_state:
                    return False
                    
                conflicts = self._check_conflicts(mod_state.instance)
                if conflicts:
                    self._resolve_conflicts(mod_state.instance, conflicts)
    
                if config:
                    mod_state.config.update(config)
                    mod_state.instance.update_config(mod_state.config)
    
                if mod_state.instance.activate():
                    mod_state.status = ModStatus.ACTIVE
                    self._active_mods[mod_id] = mod_state.instance
                    return True
                    
                mod_state.status = ModStatus.ERROR
                return False
                
            except Exception as e:
                logger.error(f"Activation failed for mod {mod_id}: {str(e)}", exc_info=True)
                mod_state.status = ModStatus.ERROR
                return False
    
    def deactivate_mod(self, mod_id: str) -> bool:
        with self._mod_lock:
            mod_state = self._mods.get(mod_id)
            if not mod_state or mod_id not in self._active_mods:
                return False

            try:
                if mod_state.instance.deactivate():
                    mod_state.status = ModStatus.INACTIVE
                    del self._active_mods[mod_id]
                    return True
                    
                mod_state.status = ModStatus.ERROR
                return False
                
            except Exception as e:
                logger.error(f"Deactivation failed for mod {mod_id}: {str(e)}", exc_info=True)
                mod_state.status = ModStatus.ERROR
                return False

    def _check_conflicts(self, mod: ModBase) -> List[str]:
        return [
            mod_id for mod_id, active_mod in self._active_mods.items()
            if (mod.priority == active_mod.priority or 
                set(mod.required_resources) & set(active_mod.required_resources))
        ]

    def _resolve_conflicts(self, new_mod: ModBase, conflicting_mod_ids: List[str]) -> None:
        for mod_id in conflicting_mod_ids:
            if mod_id in self._active_mods and new_mod.priority >= self._active_mods[mod_id].priority:
                self.deactivate_mod(mod_id)

    def get_active_mods(self) -> Dict[str, ModBase]:
        with self._mod_lock:
            return self._active_mods.copy()

    def get_all_mods(self) -> Dict[str, ModState]:
        with self._mod_lock:
            return self._mods.copy()

    def get_mod(self, mod_id: str) -> Optional[ModState]:
        with self._mod_lock:
            return self._mods.get(mod_id)

    def is_mod_active(self, mod_id: str) -> bool:
        with self._mod_lock:
            return mod_id in self._active_mods

    def get_mod_status(self, mod_id: str) -> Optional[ModStatus]:
        with self._mod_lock:
            return getattr(self._mods.get(mod_id), 'status', None)