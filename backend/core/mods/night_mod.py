from datetime import datetime, time
from typing import Optional, Dict, Any
import logging

from device_control import DeviceController
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
    
    def _apply_night_settings(self, reason: str) -> bool:
        """
        Applique les paramètres du mode nuit.
        
        Args:
            reason: Raison de l'activation ('schedule', 'idle', 'manual')
            
        Returns:
            bool: True si les paramètres ont été appliqués avec succès
        """
        try:
            brightness = 100 - self.settings["brightness_reduction"]
            blue_light = 100 - self.settings["blue_light_reduction"]
            color_temp = self.settings["color_temperature"]
            
            self.logger.info(f"Application du mode nuit (raison: {reason})")
            self.logger.info(f"Paramètres: Luminosité={brightness}%, "
                           f"Réduction lumière bleue={self.settings['blue_light_reduction']}%, "
                           f"Température de couleur={color_temp}K")
            
            # Ici on intégrerait avec les APIs du système pour changer ces paramètres
            # Par exemple:
            # - Sur Windows: via WMI ou Windows API
            # - Sur macOS: via AppleScript ou API système
            # - Sur Linux: via xrandr ou équivalent
            
            # Simuler l'application des paramètres
            if self.settings["smooth_transition"]:
                self.logger.info(f"Transition douce sur {self.settings['transition_duration_sec']} secondes")
                # Simuler une transition
                time.sleep(0.5)
            
            self.is_active = True
            self.activation_reason = reason
            self.logger.info(f"Night Mod activé avec succès (raison: {reason})")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application du mode nuit: {e}")
            return False
    
    def toggle_schedule(self, enabled: bool) -> None:
        """
        Active ou désactive le schedule automatique.
        
        Args:
            enabled: True pour activer, False pour désactiver
        """
        self.settings["auto_schedule"] = enabled
        self.logger.info(f"Schedule automatique {'activé' if enabled else 'désactivé'}")
    
    def set_schedule(self, start_time: str, end_time: str) -> bool:
        """
        Définit les heures de début et de fin du mode nuit.
        
        Args:
            start_time: Heure de début au format HH:MM
            end_time: Heure de fin au format HH:MM
            
        Returns:
            bool: True si les horaires sont valides
        """
        # Valider le format des heures
        try:
            # Vérifier le format HH:MM
            for time_str in [start_time, end_time]:
                hours, minutes = map(int, time_str.split(':'))
                if not (0 <= hours < 24 and 0 <= minutes < 60):
                    raise ValueError("Format d'heure invalide")
                    
            self.settings["start_time"] = start_time
            self.settings["end_time"] = end_time
            self.logger.info(f"Schedule mis à jour: {start_time} - {end_time}")
            return True
        except Exception as e:
            self.logger.error(f"Format d'heure invalide: {e}")
            return False