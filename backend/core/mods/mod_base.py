from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import json
import os
from pathlib import Path

class ModBase(ABC):
    """
    Base class for all mods. Provides common functionality and
    defines the interface that all mods must implement.
    """
    
    def __init__(self, mod_id: str, name: str, description: str):
        self.mod_id = mod_id
        self.name = name
        self.description = description
        self.enabled = False
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"mod.{mod_id}")
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the mod. This is called when the mod is enabled.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Shutdown the mod. This is called when the mod is disabled.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the mod.
        
        Returns:
            Dictionary containing status information
        """
        pass
    
    def enable(self) -> bool:
        """
        Enable the mod.
        
        Returns:
            True if the mod was successfully enabled, False otherwise
        """
        if self.enabled:
            self.logger.info(f"Mod '{self.name}' is already enabled")
            return True
            
        self.logger.info(f"Enabling mod '{self.name}'")
        success = self.initialize()
        if success:
            self.enabled = True
            self.logger.info(f"Mod '{self.name}' enabled successfully")
        else:
            self.logger.error(f"Failed to enable mod '{self.name}'")
        
        return success
    
    def disable(self) -> bool:
        """
        Disable the mod.
        
        Returns:
            True if the mod was successfully disabled, False otherwise
        """
        if not self.enabled:
            self.logger.info(f"Mod '{self.name}' is already disabled")
            return True
            
        self.logger.info(f"Disabling mod '{self.name}'")
        success = self.shutdown()
        if success:
            self.enabled = False
            self.logger.info(f"Mod '{self.name}' disabled successfully")
        else:
            self.logger.error(f"Failed to disable mod '{self.name}'")
        
        return success
    
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to the configuration file. If None, use default location.
            
        Returns:
            True if the configuration was loaded successfully, False otherwise
        """
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            config_path = os.path.join(base_dir, "data", "mods", f"{self.mod_id}.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                self.logger.info(f"Loaded configuration for mod '{self.name}'")
                return True
            else:
                self.logger.warning(f"No configuration file found for mod '{self.name}' at {config_path}")
                return False
        except Exception as e:
            self.logger.error(f"Error loading configuration for mod '{self.name}': {e}")
            return False
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_path: Path to the configuration file. If None, use default location.
            
        Returns:
            True if the configuration was saved successfully, False otherwise
        """
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            config_path = os.path.join(base_dir, "data", "mods", f"{self.mod_id}.json")
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"Saved configuration for mod '{self.name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration for mod '{self.name}': {e}")
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update the mod configuration.
        
        Args:
            new_config: New configuration to apply
            
        Returns:
            True if the configuration was updated successfully, False otherwise
        """
        self.config.update(new_config)
        return self.save_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the mod to a dictionary for API responses.
        
        Returns:
            Dictionary representation of the mod
        """
        return {
            "id": self.mod_id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "status": self.get_status(),
            "config": self.config
        }