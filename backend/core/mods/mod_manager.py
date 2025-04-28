import logging
from typing import Dict, Any, Optional, List
from enum import Enum, auto
import threading
import time

class ModPriority(Enum):
    CRITICAL = 100
    HIGH = 75
    MEDIUM = 50
    LOW = 25
    BACKGROUND = 10

class ModConflictResolutionStrategy(Enum):
    PRIORITY = auto()  # Highest priority mod wins
    LAST_ACTIVATED = auto()  # Most recently activated mod wins
    CUMULATIVE = auto()  # Combine mod effects if possible
    ASK_USER = auto()  # Require user intervention

class ModManager:
    """
    Advanced Mod Management System with Conflict Resolution
    """
    def __init__(self):
        self._mods: Dict[str, Any] = {}
        self._active_mods: List[str] = []
        self._mod_lock = threading.Lock()
        self._conflict_strategy = ModConflictResolutionStrategy.PRIORITY
        self.logger = logging.getLogger(__name__)

    def register_mod(self, mod_id: str, mod_instance: Any, priority: ModPriority = ModPriority.MEDIUM):
        """
        Register a new mod with priority and potential conflict handling
        
        Args:
            mod_id (str): Unique identifier for the mod
            mod_instance (Any): Mod implementation
            priority (ModPriority): Mod's operational priority
        """
        with self._mod_lock:
            # Check for existing mod
            if mod_id in self._mods:
                self.logger.warning(f"Mod {mod_id} already exists. Replacing.")
            
            # Validate mod has required methods
            required_methods = ['activate', 'deactivate']
            for method in required_methods:
                if not hasattr(mod_instance, method):
                    raise ValueError(f"Mod {mod_id} must implement {method} method")
            
            self._mods[mod_id] = {
                'instance': mod_instance,
                'priority': priority,
                'last_activated': None
            }

    def activate_mod(self, mod_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Activate a mod with advanced conflict resolution
        
        Args:
            mod_id (str): Mod to activate
            context (dict, optional): Context for mod activation
        
        Returns:
            bool: Whether mod activation was successful
        """
        with self._mod_lock:
            # Validate mod exists
            if mod_id not in self._mods:
                self.logger.error(f"Mod {mod_id} not registered")
                return False

            # Check for conflicts with active mods
            conflicting_mods = self._check_mod_conflicts(mod_id)
            
            if conflicting_mods:
                # Resolve conflicts based on strategy
                resolution_result = self._resolve_mod_conflicts(mod_id, conflicting_mods)
                
                if not resolution_result:
                    self.logger.warning(f"Could not resolve conflicts for mod {mod_id}")
                    return False

            # Attempt to activate the mod
            try:
                mod_instance = self._mods[mod_id]['instance']
                activation_success = mod_instance.activate(context)
                
                if activation_success:
                    # Update active mods and activation time
                    if mod_id not in self._active_mods:
                        self._active_mods.append(mod_id)
                    self._mods[mod_id]['last_activated'] = time.time()
                    
                    self.logger.info(f"Mod {mod_id} activated successfully")
                    return True
                else:
                    self.logger.warning(f"Mod {mod_id} activation failed")
                    return False
            
            except Exception as e:
                self.logger.error(f"Error activating mod {mod_id}: {e}")
                return False

    def deactivate_mod(self, mod_id: str) -> bool:
        """
        Deactivate a specific mod
        
        Args:
            mod_id (str): Mod to deactivate
        
        Returns:
            bool: Whether deactivation was successful
        """
        with self._mod_lock:
            if mod_id not in self._mods:
                self.logger.error(f"Mod {mod_id} not registered")
                return False

            if mod_id not in self._active_mods:
                self.logger.warning(f"Mod {mod_id} is not active")
                return True

            try:
                mod_instance = self._mods[mod_id]['instance']
                deactivation_success = mod_instance.deactivate()
                
                if deactivation_success:
                    self._active_mods.remove(mod_id)
                    self.logger.info(f"Mod {mod_id} deactivated successfully")
                    return True
                else:
                    self.logger.warning(f"Mod {mod_id} deactivation failed")
                    return False
            
            except Exception as e:
                self.logger.error(f"Error deactivating mod {mod_id}: {e}")
                return False

    def _check_mod_conflicts(self, new_mod_id: str) -> List[str]:
        """
        Check for potential conflicts with active mods
        
        Args:
            new_mod_id (str): ID of mod to be activated
        
        Returns:
            List of conflicting mod IDs
        """
        conflicting_mods = []
        new_mod_priority = self._mods[new_mod_id]['priority']

        for active_mod_id in self._active_mods:
            active_mod_priority = self._mods[active_mod_id]['priority']
            
            # Simple conflict detection based on priority
            if (new_mod_priority > active_mod_priority and 
                self._conflict_strategy == ModConflictResolutionStrategy.PRIORITY):
                conflicting_mods.append(active_mod_id)
        
        return conflicting_mods

    def _resolve_mod_conflicts(self, new_mod_id: str, conflicting_mods: List[str]) -> bool:
        """
        Resolve conflicts between mods based on selected strategy
        
        Args:
            new_mod_id (str): ID of mod to be activated
            conflicting_mods (List[str]): List of conflicting mod IDs
        
        Returns:
            bool: Whether conflict resolution was successful
        """
        if self._conflict_strategy == ModConflictResolutionStrategy.PRIORITY:
            # Deactivate lower priority mods
            for conflict_mod_id in conflicting_mods:
                self.deactivate_mod(conflict_mod_id)
            return True
        
        elif self._conflict_strategy == ModConflictResolutionStrategy.LAST_ACTIVATED:
            # Deactivate previously activated mods
            for conflict_mod_id in conflicting_mods:
                self.deactivate_mod(conflict_mod_id)
            return True
        
        elif self._conflict_strategy == ModConflictResolutionStrategy.CUMULATIVE:
            # This would require more complex mod interaction logic
            self.logger.warning("Cumulative mod resolution not fully implemented")
            return False
        
        elif self._conflict_strategy == ModConflictResolutionStrategy.ASK_USER:
            # In a real application, this would trigger a user prompt
            self.logger.warning("User intervention required for mod conflict")
            return False
        
        return False

    def get_active_mods(self) -> List[str]:
        """
        Get list of currently active mods
        
        Returns:
            List of active mod IDs
        """
        return self._active_mods.copy()

    def set_conflict_strategy(self, strategy: ModConflictResolutionStrategy):
        """
        Set the conflict resolution strategy
        
        Args:
            strategy (ModConflictResolutionStrategy): Desired conflict resolution strategy
        """
        self._conflict_strategy = strategy
        self.logger.info(f"Conflict resolution strategy set to {strategy}")