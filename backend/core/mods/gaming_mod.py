"""
Gaming Mode Module
Optimizes system configurations for the best gaming experience.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import asyncio

from ..device_control import DeviceManager
from ...db import crud

logger = logging.getLogger(__name__)

class GamingMod:
    """
    Gaming mode adjusts lighting, sound, and other settings for an optimal gaming experience.
    This includes turning on LED backlighting, adjusting audio settings, and potential 
    integration with game APIs for responsive lighting effects.
    """
    
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.active = False
        self.config_path = Path("data/mods/gaming_config.json")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load gaming mode configuration settings."""
        if not self.config_path.exists():
            default_config = {
                "led_brightness": 80,
                "led_color": "#3080FF",  # Gaming blue
                "audio_boost": True,
                "notification_silence": True,
                "preset_scenes": {
                    "fps": {"led_color": "#FF3030", "led_pattern": "pulse"},
                    "rpg": {"led_color": "#30FF80", "led_pattern": "ambient"},
                    "racing": {"led_color": "#FFFF30", "led_pattern": "chase"}
                }
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load gaming mode config: {e}")
            return {}

    async def activate(self, preset: Optional[str] = None) -> bool:
        """
        Activate gaming mode with optional preset
        
        Args:
            preset: Optional preset name (fps, rpg, racing, etc.)
            
        Returns:
            bool: Success status
        """
        try:
            # Base configuration
            settings = {
                "brightness": self.config.get("led_brightness", 80),
                "color": self.config.get("led_color", "#3080FF"),
                "pattern": "solid"
            }
            
            # Apply preset if specified
            if preset and preset in self.config.get("preset_scenes", {}):
                preset_settings = self.config["preset_scenes"][preset]
                settings.update(preset_settings)
            
            # Configure lighting
            await self.device_manager.set_lights(
                brightness=settings["brightness"],
                color=settings["color"],
                pattern=settings.get("pattern", "solid")
            )
            
            # Configure audio
            if self.config.get("audio_boost", False):
                await self.device_manager.set_audio(volume=80, equalizer="gaming")
                
            # Silence notifications if configured
            if self.config.get("notification_silence", False):
                await self.device_manager.set_notifications(enabled=False)
            
            # Log activation
            await crud.create_mod_log(
                mod_name="gaming",
                status="activated",
                settings=settings
            )
            
            self.active = True
            logger.info(f"Gaming mode activated with settings: {settings}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate gaming mode: {e}")
            return False
    
    async def deactivate(self) -> bool:
        """Deactivate gaming mode and restore normal settings"""
        try:
            # Restore default lighting
            await self.device_manager.set_lights(
                brightness=50,
                color="#FFFFFF",
                pattern="solid"
            )
            
            # Restore audio settings
            await self.device_manager.set_audio(volume=50, equalizer="normal")
            
            # Re-enable notifications
            await self.device_manager.set_notifications(enabled=True)
            
            # Log deactivation
            await crud.create_mod_log(
                mod_name="gaming",
                status="deactivated",
                settings={}
            )
            
            self.active = False
            logger.info("Gaming mode deactivated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate gaming mode: {e}")
            return False
    
    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update the gaming mode configuration"""
        try:
            # Merge new config with existing
            self.config.update(new_config)
            
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            # If already active, reapply settings
            if self.active:
                await self.deactivate()
                await self.activate()
                
            logger.info(f"Gaming mode config updated: {new_config}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update gaming mode config: {e}")
            return False