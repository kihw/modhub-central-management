from typing import Dict, Any, List, Optional
import logging
from core.mods.mod_base import ModBase
import time

class GamingMod(ModBase):
    """
    Mod optimisant les périphériques pour le gaming en fonction du jeu détecté.
    Ajuste: DPI souris, couleurs RGB, profils clavier, etc.
    """
    
    def __init__(self):
        super().__init__(
            name="Gaming Mod", 
            description="Optimise vos périphériques pour le gaming", 
            priority=100  # Priorité élevée
        )
        
        # Configuration par défaut
        self.settings = {
            "default_dpi": 800,
            "default_polling_rate": 1000,
            "enable_rgb": True,
            "game_profiles": {},  # Sera rempli avec des profils spécifiques aux jeux
            "peripherals": {
                "keyboard": {"enabled": True},
                "mouse": {"enabled": True},
                "headset": {"enabled": True},
                "monitor": {"enabled": True}
            }
        }
        
        # État actuel
        self.current_game = None
        self.applied_profile = None
    
    def activate(self, context: Dict[str, Any] = None) -> bool:
        """
        Active le mode gaming en fonction du contexte.
        
        Args:
            context: Dictionnaire contenant le contexte du système, notamment les processus en cours
                    d'exécution pour détecter les jeux
        """
        if not context:
            self.logger.warning("Aucun contexte fourni pour Gaming Mod, utilisation des paramètres par défaut")
            return self._apply_default_profile()
        
        # Détecter le jeu en cours d'exécution
        detected_game = self._detect_game(context.get("processes", []))
        
        if detected_game:
            self.current_game = detected_game
            success = self._apply_game_profile(detected_game)
            if success:
                self.is_active = True
                self.logger.info(f"Gaming Mod activé pour: {detected_game}")
                return True
        
        # Si aucun jeu spécifique n'est détecté mais qu'on a détecté une activité gaming
        if context.get("is_gaming_activity", False):
            return self._apply_default_profile()
        
        # Pas de contexte de jeu
        self.logger.info("Pas de jeu détecté, Gaming Mod ne sera pas activé")
        return False
    
    def deactivate(self) -> bool:
        """Désactive le mode gaming et restaure les paramètres par défaut."""
        if not self.is_active:
            return True
        
        try:
            # Restaurer les paramètres par défaut du système pour les périphériques
            # (Ici on simulerait l'interaction avec les SDK des périphériques)
            self.logger.info("Restauration des paramètres par défaut pour les périphériques")
            
            # Simulation de restauration des paramètres
            time.sleep(0.5)  # Simuler un traitement
            
            self.is_active = False
            self.current_game = None
            self.applied_profile = None
            
            self.logger.info("Gaming Mod désactivé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la désactivation de Gaming Mod: {e}")
            return False
    
    def _detect_game(self, processes: List[Dict[str, Any]]) -> Optional[str]:
        """
        Détecte un jeu parmi les processus en cours d'exécution.
        
        Args:
            processes: Liste des processus en cours d'exécution
            
        Returns:
            str: Nom du jeu détecté ou None
        """
        # Dictionnaire des noms de processus connus pour les jeux
        game_processes = {
            "csgo.exe": "Counter-Strike: Global Offensive",
            "valorant.exe": "Valorant",
            "overwatch.exe": "Overwatch",
            "rocketleague.exe": "Rocket League",
            "gta5.exe": "Grand Theft Auto V",
            "FortniteClient-Win64-Shipping.exe": "Fortnite",
            "r5apex.exe": "Apex Legends",
            "Cyberpunk2077.exe": "Cyberpunk 2077",
            # Ajouter d'autres jeux au besoin
        }
        
        # Vérifier si l'un des processus en cours correspond à un jeu connu
        for process in processes:
            process_name = process.get("name", "").lower()
            for game_process, game_name in game_processes.items():
                if game_process.lower() in process_name:
                    return game_name
        
        return None
    
    def _apply_game_profile(self, game_name: str) -> bool:
        """
        Applique un profil spécifique pour un jeu.
        
        Args:
            game_name: Nom du jeu détecté
            
        Returns:
            bool: True si le profil a été appliqué avec succès
        """
        # Récupérer le profil pour ce jeu ou utiliser le profil par défaut
        game_profiles = self.settings.get("game_profiles", {})
        profile = game_profiles.get(game_name, {})
        
        if not profile:
            self.logger.info(f"Aucun profil spécifique pour {game_name}, utilisation du profil par défaut")
            return self._apply_default_profile()
        
        try:
            # Ici on appliquerait réellement les paramètres aux périphériques
            # en utilisant les SDK appropriés
            
            # Appliquer les paramètres de la souris
            mouse_settings = profile.get("mouse", {})
            if mouse_settings and self.settings["peripherals"]["mouse"]["enabled"]:
                dpi = mouse_settings.get("dpi", self.settings["default_dpi"])
                polling_rate = mouse_settings.get("polling_rate", self.settings["default_polling_rate"])
                self.logger.info(f"Application des paramètres souris: DPI={dpi}, Polling={polling_rate}")
                # Simuler l'appel au SDK de la souris
            
            # Appliquer les paramètres du clavier
            keyboard_settings = profile.get("keyboard", {})
            if keyboard_settings and self.settings["peripherals"]["keyboard"]["enabled"]:
                rgb_profile = keyboard_settings.get("rgb_profile", "default")
                macro_profile = keyboard_settings.get("macro_profile", "default")
                self.logger.info(f"Application des paramètres clavier: RGB={rgb_profile}, Macros={macro_profile}")
                # Simuler l'appel au SDK du clavier
            
            # Appliquer d'autres paramètres selon les périphériques...
            
            self.applied_profile = game_name
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application du profil pour {game_name}: {e}")
            return False
    
    def _apply_default_profile(self) -> bool:
        """
        Applique le profil par défaut pour le gaming.
        
        Returns:
            bool: True si le profil a été appliqué avec succès
        """
        try:
            # Application des paramètres par défaut
            default_dpi = self.settings["default_dpi"]
            default_polling = self.settings["default_polling_rate"]
            
            self.logger.info(f"Application du profil gaming par défaut: DPI={default_dpi}, Polling={default_polling}")
            
            # Simulation d'application des paramètres
            time.sleep(0.5)
            
            self.is_active = True
            self.applied_profile = "default"
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application du profil par défaut: {e}")
            return False
    
    def update_game_profile(self, game_name: str, profile: Dict[str, Any]) -> bool:
        """
        Met à jour ou crée un profil spécifique pour un jeu.
        
        Args:
            game_name: Nom du jeu
            profile: Paramètres du profil
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            if "game_profiles" not in self.settings:
                self.settings["game_profiles"] = {}
                
            self.settings["game_profiles"][game_name] = profile
            self.logger.info(f"Profil mis à jour pour {game_name}")
            
            # Si ce jeu est actuellement en cours, appliquer les nouveaux paramètres
            if self.is_active and self.current_game == game_name:
                return self._apply_game_profile(game_name)
                
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du profil pour {game_name}: {e}")
            return False