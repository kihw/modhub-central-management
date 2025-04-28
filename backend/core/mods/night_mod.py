from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime, time as dt_time
from .mod_base import ModBase

class NightMod(ModBase):
    """
    Mod qui ajuste la luminosité et les couleurs pour réduire la fatigue oculaire 
    en soirée/nuit ou pendant les périodes d'inactivité.
    """
    
    def __init__(self):
        super().__init__(
            name="Night Mod", 
            description="Réduit la fatigue oculaire en ajustant la luminosité et les couleurs", 
            priority=50  # Priorité moyenne (inférieure à Gaming Mod)
        )
        
        # Configuration par défaut
        self.settings = {
            "auto_schedule": True,
            "start_time": "20:00",  # Format HH:MM (24h)
            "end_time": "07:00",    # Format HH:MM (24h)
            "idle_activation": True,
            "idle_time_minutes": 15,  # Activer après X minutes d'inactivité
            "brightness_reduction": 30,  # Pourcentage
            "blue_light_reduction": 60,  # Pourcentage
            "color_temperature": 2700,   # Kelvin (plus bas = plus chaud/jaune)
            "smooth_transition": True,
            "transition_duration_sec": 30
        }
        
        # État actuel
        self.activation_reason = None  # 'schedule', 'idle', 'manual'
    
    def activate(self, context: Dict[str, Any] = None) -> bool:
        """
        Active le Night Mod selon le contexte (heure, inactivité).
        
        Args:
            context: Dictionnaire contenant le contexte du système (heure, inactivité, etc.)
            
        Returns:
            bool: True si l'activation a réussi
        """
        if not context:
            self.logger.warning("Aucun contexte fourni pour Night Mod, utilisation des paramètres par défaut")
            return self._apply_night_settings(reason="manual")
        
        # Vérifier si l'heure actuelle est dans la plage de schedule
        should_activate_by_schedule = False
        if self.settings["auto_schedule"]:
            current_time = context.get("current_time", datetime.now().time())
            should_activate_by_schedule = self._is_night_time(current_time)
            
        # Vérifier si l'utilisateur est inactif depuis assez longtemps
        should_activate_by_idle = False
        if self.settings["idle_activation"]:
            idle_time_min = context.get("idle_time_minutes", 0)
            should_activate_by_idle = idle_time_min >= self.settings["idle_time_minutes"]
        
        # Activer si l'une des conditions est remplie
        if should_activate_by_schedule:
            return self._apply_night_settings(reason="schedule")
        elif should_activate_by_idle:
            return self._apply_night_settings(reason="idle")
        else:
            # Ne pas activer le mode nuit si aucune condition n'est remplie
            if self.is_active:
                self.logger.info("Les conditions pour Night Mod ne sont plus remplies, désactivation...")
                return self.deactivate()
            return False
    
    def deactivate(self) -> bool:
        """
        Désactive le Night Mod et restaure les paramètres normaux.
        
        Returns:
            bool: True si la désactivation a réussi
        """
        if not self.is_active:
            return True
            
        try:
            # Simuler la restauration des paramètres d'affichage normaux
            self.logger.info("Restauration des paramètres d'affichage normaux...")
            
            # Avec transition douce si activée
            if self.settings["smooth_transition"]:
                self.logger.info(f"Transition douce sur {self.settings['transition_duration_sec']} secondes")
                # Simuler une transition
                time.sleep(0.5)
            else:
                # Changement immédiat
                pass
                
            self.is_active = False
            self.activation_reason = None
            self.logger.info("Night Mod désactivé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la désactivation de Night Mod: {e}")
            return False
    
    def _is_night_time(self, current_time: datetime.time) -> bool:
        """
        Vérifie si l'heure actuelle est dans la plage de schedule du mode nuit.
        
        Args:
            current_time: Heure actuelle
            
        Returns:
            bool: True si c'est la "nuit" selon le schedule
        """
        # Convertir les string de temps en objets time
        start_hour, start_minute = map(int, self.settings["start_time"].split(':'))
        end_hour, end_minute = map(int, self.settings["end_time"].split(':'))
        
        start_time = dt_time(start_hour, start_minute)
        end_time = dt_time(end_hour, end_minute)
        
        # Si l'heure de fin est avant l'heure de début, cela signifie que la période
        # s'étend sur deux jours (ex: 22:00 à 07:00)
        if end_time < start_time:
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