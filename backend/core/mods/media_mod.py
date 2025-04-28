import logging
from typing import Dict, Any, List, Optional

from ..device_control import DeviceController

logger = logging.getLogger(__name__)

class MediaMod:
    """
    Media Mod controls lighting and devices to create the optimal 
    environment for watching movies, playing games, or listening to music.
    It can adjust lighting, control A/V equipment, and reduce distractions.
    """
    
    def __init__(self, device_controller: DeviceController):
        self.device_controller = device_controller
        self.active = False
        self.current_scene = None
        self.settings = {}
        self.scenes = {}
        self.load_settings()
        
    def load_settings(self) -> None:
        """Load media mod settings and scenes from database"""
        try:
            # Default settings if not found in DB
            self.settings = {
                "default_scene": "movie",
                "affect_rooms": ["living_room"],
                "auto_restore": True,
                "pause_notifications": True
            }
            
            # Default scenes
            self.scenes = {
                "movie": {
                    "lights": {
                        "brightness": 10,
                        "color": "blue",
                        "enabled_lights": ["ambient"]
                    },
                    "devices": {
                        "tv": {"power": True, "input": "hdmi1"},
                        "soundbar": {"power": True, "volume": 60},
                        "blinds": {"position": "closed"}
                    }
                },
                "gaming": {
                    "lights": {
                        "brightness": 40,
                        "color": "purple",
                        "enabled_lights": ["overhead", "ambient"]
                    },
                    "devices": {
                        "tv": {"power": True, "input": "hdmi2", "mode": "game"},
                        "soundbar": {"power": True, "volume": 50},
                        "blinds": {"position": "partial"}
                    }
                },
                "music": {
                    "lights": {
                        "brightness": 60,
                        "color": "green",
                        "color_mode": "flow",
                        "enabled_lights": ["all"]
                    },
                    "devices": {
                        "tv": {"power": False},
                        "soundbar": {"power": True, "volume": 70, "eq": "music"},
                        "blinds": {"position": "open"}
                    }
                }
            }
            
            # TODO: Load from actual DB when implemented
            logger.info("Media mod settings loaded")
        except Exception as e:
            logger.error(f"Error loading media mod settings: {e}")
    
    def activate(self, scene_name: Optional[str] = None) -> bool:
        """
        Activate media mode with the specified scene or default scene
        
        Args:
            scene_name: The scene to activate (movie, gaming, music, etc.)
        
        Returns:
            bool: Success status
        """
        try:
            # Use specified scene or default
            scene_to_use = scene_name or self.settings.get("default_scene")
            
            if scene_to_use not in self.scenes:
                logger.error(f"Scene {scene_to_use} not found")
                return False
                
            scene = self.scenes[scene_to_use]
            affected_rooms = self.settings.get("affect_rooms", ["living_room"])
            
            # Save current state to restore later if auto_restore is enabled
            if self.settings.get("auto_restore", True):
                self._save_current_state(affected_rooms)
                
            # Configure lighting
            light_config = scene.get("lights", {})
            brightness = light_config.get("brightness", 50)
            color = light_config.get("color")
            enabled_lights = light_config.get("enabled_lights", ["all"])
            
            # Apply lighting changes
            for room_name in affected_rooms:
                lights = self._get_lights_in_room(room_name)
                
                for light in lights:
                    # Skip lights not in enabled list, unless "all" is specified
                    if "all" not in enabled_lights and light.name not in enabled_lights:
                        self.device_controller.set_device_state(light.id, state=False)
                        continue
                        
                    # Apply light settings
                    light_params = {
                        "state": True,
                        "brightness": brightness
                    }
                    
                    if color:
                        light_params["color"] = color
                        
                    self.device_controller.set_device_state(light.id, **light_params)
            
            # Configure devices
            device_config = scene.get("devices", {})
            for device_name, device_settings in device_config.items():
                device = self.device_controller.get_device_by_name(device_name)
                if device:
                    self.device_controller.set_device_state(device.id, **device_settings)
            
            # Update state
            self.active = True
            self.current_scene = scene_to_use
            
            if self.settings.get("pause_notifications", True):
                # TODO: Implement notification pausing
                pass
                
            logger.info(f"Media mod activated with scene: {scene_to_use}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating media mod: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate media mode and restore previous state if auto_restore enabled"""
        if not self.active:
            logger.info("Media mod already inactive")
            return True
            
        try:
            affected_rooms = self.settings.get("affect_rooms", ["living_room"])
            
            if self.settings.get("auto_restore", True):
                self._restore_previous_state()
            else:
                # Just turn everything back to normal
                for room_name in affected_rooms:
                    lights = self._get_lights_in_room(room_name)
                    
                    for light in lights:
                        self.device_controller.set_device_state(
                            device_id=light.id,
                            state=True,
                            brightness=100,
                            color="white"
                        )
            
            # Resume notifications if they were paused
            if self.settings.get("pause_notifications", True):
                # TODO: Resume notifications
                pass
                
            self.active = False
            self.current_scene = None
            logger.info("Media mod deactivated")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating media mod: {e}")
            return False
    
    def add_scene(self, scene_name: str, scene_config: Dict[str, Any]) -> bool:
        """Add a new scene or update an existing one"""
        try:
            self.scenes[scene_name] = scene_config
            # TODO: Save to database
            logger.info(f"Scene {scene_name} added/updated")
            return True
        except Exception as e:
            logger.error(f"Error adding scene {scene_name}: {e}")
            return False
    
    def remove_scene(self, scene_name: str) -> bool:
        """Remove a scene"""
        try:
            if scene_name in self.scenes:
                del self.scenes[scene_name]
                # TODO: Delete from database
                logger.info(f"Scene {scene_name} removed")
                return True
            logger.warning(f"Scene {scene_name} not found")
            return False
        except Exception as e:
            logger.error(f"Error removing scene {scene_name}: {e}")
            return False
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update media mod settings"""
        try:
            self.settings.update(new_settings)
            # TODO: Save to database
            logger.info("Media mod settings updated")
            return True
        except Exception as e:
            logger.error(f"Error updating media mod settings: {e}")
            return False
    
    def _get_lights_in_room(self, room_name: str) -> List[Any]:
        """Get all lights in the specified room"""
        devices = self.device_controller.get_devices_by_room(room_name)
        return [d for d in devices if d.type == "light"]
    
    def _save_current_state(self, rooms: List[str]) -> None:
        """Save current state of devices to restore later"""
        self.previous_state = {}
        
        for room_name in rooms:
            devices = self.device_controller.get_devices_by_room(room_name)
            
            for device in devices:
                # Save current state
                self.previous_state[device.id] = self.device_controller.get_device_state(device.id)
    
    def _restore_previous_state(self) -> None:
        """Restore devices to their previous state"""
        if not hasattr(self, 'previous_state') or not self.previous_state:
            logger.warning("No previous state to restore")
            return
            
        for device_id, state in self.previous_state.items():
            self.device_controller.set_device_state(device_id, **state)
        
        self.previous_state = {}