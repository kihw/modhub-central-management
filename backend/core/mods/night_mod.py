from datetime import datetime, time
from typing import Optional, Dict, Any
import logging
import time as time_module

# Import modifié pour éviter l'erreur de module non trouvé
# from device_control import DeviceController - cette ligne causait l'erreur
# Utilisons une classe fictive pour le développement
class DeviceController:
    """Classe temporaire pour remplacer l'import manquant"""
    def __init__(self, *args, **kwargs):
        pass

logger = logging.getLogger(__name__)

class NightMod:
    """
    Night Mod controls lighting based on time of day to create a comfortable
    nighttime environment with reduced brightness and warmer colors.
    """
    
    def __init__(self, device_controller=None):
        self.device_controller = device_controller or DeviceController()
        self.active = False
        self.settings = {}
        self.logger = logging.getLogger(__name__)
        self.load_settings()
        self.activation_reason = None
        self.is_active = False
        
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
                "exclude_rooms": [],
                "brightness_reduction": 40,  # %
                "blue_light_reduction": 80,  # %
                "color_temperature": 2700,   # Kelvin
                "smooth_transition": True,
                "transition_duration_sec": 30,
                "auto_schedule": True,       # Activer selon l'horaire
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
                time_module.sleep(0.5)
            
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
            
    def activate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Activer le Night Mod (requis par l'interface ModBase)
        
        Args:
            context: Contexte d'activation (optionnel)
        
        Returns:
            bool: True si l'activation a réussi
        """
        return self._apply_night_settings("manual" if not context else "auto")
    
    def deactivate(self) -> bool:
        """
        Désactiver le Night Mod (requis par l'interface ModBase)
        
        Returns:
            bool: True si la désactivation a réussi
        """
        try:
            self.logger.info("Désactivation du Night Mod")
            # Simuler la restauration des paramètres
            time_module.sleep(0.5)
            self.is_active = False
            self.activation_reason = None
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la désactivation du Night Mod: {e}")
            return False