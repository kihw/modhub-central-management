from datetime import datetime, time
from typing import Optional, Dict, Any
import logging
import time as time_module

logger = logging.getLogger(__name__)

class DeviceController:
    def __init__(self):
        self.devices = {}
        self._verify_connection()

    def _verify_connection(self) -> None:
        pass

    def adjust_brightness(self, level: int) -> bool:
        level = max(0, min(100, level))
        return True

    def adjust_color_temp(self, temp: int) -> bool:
        temp = max(1000, min(10000, temp))
        return True

    def apply_room_settings(self, room: str, settings: Dict[str, Any]) -> bool:
        if not room or not settings:
            return False
        return True

class NightMod:
    DEFAULT_SETTINGS = {
        "start_time": "22:00",
        "end_time": "06:00",
        "brightness_level": 30,
        "color_temp": 2700,
        "affect_rooms": ["bedroom", "living_room", "hallway"],
        "exclude_rooms": [],
        "brightness_reduction": 40,
        "blue_light_reduction": 80,
        "color_temperature": 2700,
        "smooth_transition": True,
        "transition_duration_sec": 30,
        "auto_schedule": True,
    }

    def __init__(self, device_controller: Optional[DeviceController] = None):
        self.device_controller = device_controller or DeviceController()
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.logger = logging.getLogger(__name__)
        self.activation_reason = None
        self.is_active = False
        
    def load_settings(self) -> None:
        try:
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.logger.info("Night mod settings loaded")
        except Exception as e:
            self.logger.error(f"Error loading night mod settings: {e}")
    
    def is_night_time(self) -> bool:
        current_time = datetime.now().time()
        try:
            start_time = datetime.strptime(self.settings["start_time"], "%H:%M").time()
            end_time = datetime.strptime(self.settings["end_time"], "%H:%M").time()
            
            if start_time > end_time:
                return current_time >= start_time or current_time <= end_time
            return start_time <= current_time <= end_time
        except ValueError:
            self.logger.error("Invalid time format in settings")
            return False
    
    def _apply_night_settings(self, reason: str) -> bool:
        if not self.device_controller:
            self.logger.error("Device controller not initialized")
            return False

        try:
            brightness = max(0, min(100 - self.settings["brightness_reduction"], 100))
            blue_light = max(0, min(100 - self.settings["blue_light_reduction"], 100))
            color_temp = self.settings["color_temperature"]
            
            if self.settings["smooth_transition"]:
                transition_time = min(self.settings["transition_duration_sec"], 300)
                time_module.sleep(transition_time / 60)
            
            affected_rooms = set(self.settings["affect_rooms"]) - set(self.settings["exclude_rooms"])
            for room in affected_rooms:
                self.device_controller.apply_room_settings(room, {
                    "brightness": brightness,
                    "color_temp": color_temp,
                    "blue_light": blue_light
                })
            
            self.is_active = True
            self.activation_reason = reason
            self.logger.info(f"Night Mod activated: brightness={brightness}%, blue_light={blue_light}%, color_temp={color_temp}K")
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply night settings: {e}")
            return False
    
    def toggle_schedule(self, enabled: bool) -> None:
        self.settings["auto_schedule"] = bool(enabled)
        self.logger.info(f"Auto schedule {'enabled' if enabled else 'disabled'}")
    
    def set_schedule(self, start_time: str, end_time: str) -> bool:
        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            self.settings["start_time"] = start_time
            self.settings["end_time"] = end_time
            return True
        except ValueError:
            self.logger.error("Invalid time format")
            return False
            
    def activate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        if self.is_active:
            return True
        return self._apply_night_settings("manual" if context is None else "auto")
    
    def deactivate(self) -> bool:
        if not self.is_active:
            return True
        try:
            if self.settings["smooth_transition"]:
                transition_time = min(self.settings["transition_duration_sec"], 300)
                time_module.sleep(transition_time / 60)

            for room in self.settings["affect_rooms"]:
                if room not in self.settings["exclude_rooms"]:
                    self.device_controller.apply_room_settings(room, {
                        "brightness": 100,
                        "color_temp": 6500,
                        "blue_light": 100
                    })

            self.is_active = False
            self.activation_reason = None
            return True
        except Exception as e:
            self.logger.error(f"Failed to deactivate Night Mod: {e}")
            return False