from datetime import datetime, time
from typing import Optional, Dict, Any
import logging

from ..device_control import DeviceController
from ...db.models import Settings, Room

logger = logging.getLogger(__name__)

class NightMod:
    """
    Night Mod controls lighting based on time of day to create a comfortable
    nighttime environment with reduced brightness and warmer colors.
    """
    
    def __init__(self, device_controller: DeviceController):
        self.device_controller = device_controller
        self.active = False
        self.settings = {}
        self.load_settings()
        
    def load_settings(self) -> None:
        """Load night mod settings from database"""
        try:
            # Default settings if not found in DB
            self.settings = {
                "start_time": "22:00",  # 10 PM
                "end_time": "06:00",    # 6 AM
                "brightness_level": 30,  # % of normal brightness
                "color_temp": 2700,     # Kelvin (warm)
                "affect_rooms": ["bedroom", "living_room", "hallway"],
                "exclude_rooms": []
            }
            
            # TODO: Load from actual DB when implemented
            logger.info("Night mod settings loaded")
        except Exception as e:
            logger.error(f"Error loading night mod settings: {e}")
    
    def is_night_time(self) -> bool:
        """Check if current time is within night mod hours"""
        current_time = datetime.now().time()
        
        start_time_str = self.settings.get("start_time", "22:00")
        end_time_str = self.settings.get("end_time", "06:00")
        
        start_hour, start_minute = map(int, start_time_str.split(":"))
        end_hour, end_minute = map(int, end_time_str.split(":"))
        
        start_time = time(start_hour, start_minute)
        end_time = time(end_hour, end_minute)
        
        # Handle overnight periods (e.g., 22:00 to 06:00)
        if start_time > end_time:
            return current_time >= start_time or current_time <= end_time
        else:
            return start_time <= current_time <= end_time
    
    def activate(self) -> bool:
        """Activate night mode for affected rooms"""
        if self.active:
            logger.info("Night mod already active")
            return True
            
        try:
            # Get rooms to affect
            affected_rooms = self.settings.get("affect_rooms", [])
            excluded_rooms = self.settings.get("exclude_rooms", [])
            
            brightness = self.settings.get("brightness_level", 30)
            color_temp = self.settings.get("color_temp", 2700)
            
            # Apply night settings to each affected room
            for room_name in affected_rooms:
                if room_name in excluded_rooms:
                    continue
                    
                # Get lights in room
                devices = self.device_controller.get_devices_by_room(room_name)
                
                for device in devices:
                    if device.type == "light":
                        self.device_controller.set_device_state(
                            device_id=device.id,
                            state=True,  # On
                            brightness=brightness,
                            color_temp=color_temp
                        )
            
            self.active = True
            logger.info("Night mod activated")
            return True
            
        except Exception as e:
            logger.error(f"Error activating night mod: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate night mode and restore normal lighting"""
        if not self.active:
            logger.info("Night mod already inactive")
            return True
            
        try:
            # Get rooms affected
            affected_rooms = self.settings.get("affect_rooms", [])
            
            # Reset light settings in each affected room
            for room_name in affected_rooms:
                devices = self.device_controller.get_devices_by_room(room_name)
                
                for device in devices:
                    if device.type == "light":
                        # Reset to default daytime settings
                        self.device_controller.set_device_state(
                            device_id=device.id,
                            state=True,  # On
                            brightness=100,  # Full brightness
                            color_temp=4000  # Neutral white
                        )
            
            self.active = False
            logger.info("Night mod deactivated")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating night mod: {e}")
            return False
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update night mod settings"""
        try:
            self.settings.update(new_settings)
            # TODO: Save to database
            
            # If settings changed and it's nighttime, reapply settings
            if self.active or self.is_night_time():
                self.deactivate()
                self.activate()
                
            logger.info("Night mod settings updated")
            return True
        except Exception as e:
            logger.error(f"Error updating night mod settings: {e}")
            return False