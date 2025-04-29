"""
Core module for mod management in ModHub Central.
This module handles mod activation, deactivation, and conflict resolution.
"""

import logging
from typing import Dict, Any, List, Optional, Type
import threading
import time

from .mod_base import ModBase
from .gaming_mod import GamingMod
from .media_mod import MediaMod
from .night_mod import NightMod

logger = logging.getLogger(__name__)

class ModManager:
    """
    Manages mod instances, handles activation/deactivation, and resolves conflicts based on priorities.
    """
    def __init__(self):
        self._mods: Dict[str, ModBase] = {}
        self._active_mods: Dict[str, ModBase] = {}
        self._mod_lock = threading.Lock()
        self._initialize_default_mods()
        logger.info("ModManager initialized with default mods")

    def _initialize_default_mods(self):
        """Initialize and register the default system mods."""
        try:
            self.register_mod("gaming", GamingMod())
            self.register_mod("night", NightMod(None))  # Note: We'll need to fix the None device_controller later
            self.register_mod("media", MediaMod())
            logger.info("Default mods registered successfully")
        except Exception as e:
            logger.error(f"Error registering default mods: {e}")

    def register_mod(self, mod_id: str, mod_instance: ModBase) -> bool:
        """
        Register a mod with the manager.
        
        Args:
            mod_id: Unique identifier for the mod
            mod_instance: Instance of the mod
            
        Returns:
            bool: Whether registration was successful
        """
        with self._mod_lock:
            if mod_id in self._mods:
                logger.warning(f"Mod {mod_id} already registered, replacing")
            
            self._mods[mod_id] = mod_instance
            logger.info(f"Mod '{mod_id}' registered successfully")
            return True

    def unregister_mod(self, mod_id: str) -> bool:
        """
        Unregister a mod from the manager.
        
        Args:
            mod_id: ID of the mod to unregister
            
        Returns:
            bool: Whether unregistration was successful
        """
        with self._mod_lock:
            if mod_id not in self._mods:
                logger.warning(f"Mod {mod_id} not registered, cannot unregister")
                return False
            
            # If active, deactivate first
            if mod_id in self._active_mods:
                self.deactivate_mod(mod_id)
            
            del self._mods[mod_id]
            logger.info(f"Mod '{mod_id}' unregistered successfully")
            return True

    def activate_mod(self, mod_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Activate a mod with optional configuration.
        
        Args:
            mod_id: ID of the mod to activate
            config: Optional configuration to apply before activation
            
        Returns:
            bool: Whether activation was successful
        """
        with self._mod_lock:
            if mod_id not in self._mods:
                logger.error(f"Cannot activate unknown mod: {mod_id}")
                return False
            
            mod = self._mods[mod_id]
            
            # Check for conflicts with currently active mods
            conflicts = self._check_conflicts(mod)
            if conflicts:
                logger.info(f"Resolving conflicts for mod {mod_id} with: {conflicts}")
                self._resolve_conflicts(mod, conflicts)
            
            # Apply configuration if provided
            if config:
                logger.debug(f"Applying configuration to mod {mod_id}")
                mod.update_config(config)
            
            # Activate the mod
            try:
                success = mod.activate()
                if success:
                    self._active_mods[mod_id] = mod
                    logger.info(f"Mod '{mod_id}' activated successfully")
                    return True
                else:
                    logger.warning(f"Mod '{mod_id}' activation failed")
                    return False
            except Exception as e:
                logger.error(f"Error activating mod '{mod_id}': {e}")
                return False

    def deactivate_mod(self, mod_id: str) -> bool:
        """
        Deactivate a mod.
        
        Args:
            mod_id: ID of the mod to deactivate
            
        Returns:
            bool: Whether deactivation was successful
        """
        with self._mod_lock:
            if mod_id not in self._mods:
                logger.error(f"Cannot deactivate unknown mod: {mod_id}")
                return False
            
            if mod_id not in self._active_mods:
                logger.warning(f"Mod '{mod_id}' is not active, nothing to deactivate")
                return True
            
            mod = self._mods[mod_id]
            
            try:
                success = mod.deactivate()
                if success:
                    del self._active_mods[mod_id]
                    logger.info(f"Mod '{mod_id}' deactivated successfully")
                    return True
                else:
                    logger.warning(f"Mod '{mod_id}' deactivation failed")
                    return False
            except Exception as e:
                logger.error(f"Error deactivating mod '{mod_id}': {e}")
                return False

    def _check_conflicts(self, mod: ModBase) -> List[str]:
        """
        Check if a mod conflicts with any currently active mods.
        
        Args:
            mod: The mod to check for conflicts
            
        Returns:
            List of mod IDs that conflict
        """
        conflicts = []
        
        for active_mod_id, active_mod in self._active_mods.items():
            # In a real implementation, we'd have more sophisticated conflict detection
            # For now, we'll consider it a conflict if they have the same priority
            if mod.priority == active_mod.priority:
                conflicts.append(active_mod_id)
        
        return conflicts

    def _resolve_conflicts(self, new_mod: ModBase, conflicting_mod_ids: List[str]) -> None:
        """
        Resolve conflicts between mods based on priority.
        
        Args:
            new_mod: The new mod being activated
            conflicting_mod_ids: List of conflicting mod IDs
        """
        for conflicting_mod_id in conflicting_mod_ids:
            conflicting_mod = self._active_mods.get(conflicting_mod_id)
            if not conflicting_mod:
                continue
                
            # If new mod has higher priority, deactivate the conflicting mod
            if new_mod.priority > conflicting_mod.priority:
                logger.info(f"Deactivating lower-priority mod {conflicting_mod_id} due to conflict")
                self.deactivate_mod(conflicting_mod_id)
            # Otherwise the existing mod wins, and we'll let the activation fail

    def get_active_mods(self) -> Dict[str, ModBase]:
        """
        Get all currently active mods.
        
        Returns:
            Dictionary of active mod IDs to mod instances
        """
        with self._mod_lock:
            return self._active_mods.copy()

    def get_all_mods(self) -> Dict[str, ModBase]:
        """
        Get all registered mods.
        
        Returns:
            Dictionary of all mod IDs to mod instances
        """
        with self._mod_lock:
            return self._mods.copy()

    def get_mod(self, mod_id: str) -> Optional[ModBase]:
        """
        Get a specific mod instance.
        
        Args:
            mod_id: ID of the mod to retrieve
            
        Returns:
            Mod instance or None if not found
        """
        return self._mods.get(mod_id)

    def is_mod_active(self, mod_id: str) -> bool:
        """
        Check if a mod is currently active.
        
        Args:
            mod_id: ID of the mod to check
            
        Returns:
            Whether the mod is active
        """
        return mod_id in self._active_mods
