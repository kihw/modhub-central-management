# backend/core/mods/mod_manager.py
import logging
from typing import Dict, Any, Optional, List
from .mod_base import ModBase
from .gaming_mod import GamingMod
from .media_mod import MediaMod
from .night_mod import NightMod

class ModManager:
    """
    Gestionnaire central pour tous les mods.
    Permet d'activer/désactiver les mods et de gérer leurs interactions.
    """
    
    def __init__(self):
        self.mods = {}
        self.logger = logging.getLogger(__name__)
        self._init_mods()
    
    def _init_mods(self):
        """Initialise les mods intégrés"""
        # Créer les instances des mods de base
        self.mods['gaming'] = GamingMod()
        self.mods['night'] = NightMod()
        self.mods['media'] = MediaMod()
        
        self.logger.info(f"ModManager initialisé avec {len(self.mods)} mods")
    
    def register_mod(self, mod_id: str, mod_instance: ModBase) -> bool:
        """
        Enregistre un nouveau mod personnalisé
        
        Args:
            mod_id: Identifiant unique du mod
            mod_instance: Instance d'une classe dérivée de ModBase
            
        Returns:
            bool: True si l'enregistrement a réussi
        """
        if mod_id in self.mods:
            self.logger.warning(f"Le mod {mod_id} existe déjà et sera remplacé")
            
        if not isinstance(mod_instance, ModBase):
            self.logger.error(f"L'instance de mod doit hériter de ModBase")
            return False
            
        self.mods[mod_id] = mod_instance
        self.logger.info(f"Mod {mod_id} enregistré avec succès")
        return True
    
    def unregister_mod(self, mod_id: str) -> bool:
        """
        Supprime un mod du gestionnaire
        
        Args:
            mod_id: Identifiant du mod à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        if mod_id not in self.mods:
            self.logger.warning(f"Le mod {mod_id} n'existe pas")
            return False
            
        # Désactiver le mod s'il est actif
        if self.mods[mod_id].is_active:
            self.deactivate_mod(mod_id)
            
        del self.mods[mod_id]
        self.logger.info(f"Mod {mod_id} supprimé avec succès")
        return True
    
    def activate_mod(self, mod_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Active un mod avec une configuration spécifique
        
        Args:
            mod_id: Identifiant du mod à activer
            config: Configuration optionnelle à appliquer
            
        Returns:
            bool: True si l'activation a réussi
        """
        if mod_id not in self.mods:
            self.logger.error(f"Le mod {mod_id} n'existe pas")
            return False
            
        mod = self.mods[mod_id]
        
        # Appliquer la configuration si fournie
        if config:
            mod.update_settings(config)
            
        # Activer le mod
        context = self._get_system_context()
        success = mod.activate(context)
        
        if success:
            self.logger.info(f"Mod {mod_id} activé avec succès")
        else:
            self.logger.error(f"Échec de l'activation du mod {mod_id}")
            
        return success
    
    def deactivate_mod(self, mod_id: str) -> bool:
        """
        Désactive un mod
        
        Args:
            mod_id: Identifiant du mod à désactiver
            
        Returns:
            bool: True si la désactivation a réussi
        """
        if mod_id not in self.mods:
            self.logger.error(f"Le mod {mod_id} n'existe pas")
            return False
            
        mod = self.mods[mod_id]
        
        if not mod.is_active:
            self.logger.info(f"Le mod {mod_id} est déjà inactif")
            return True
            
        success = mod.deactivate()
        
        if success:
            self.logger.info(f"Mod {mod_id} désactivé avec succès")
        else:
            self.logger.error(f"Échec de la désactivation du mod {mod_id}")
            
        return success
    
    def get_active_mods(self) -> List[str]:
        """
        Retourne la liste des mods actifs
        
        Returns:
            List[str]: Liste des identifiants des mods actifs
        """
        return [mod_id for mod_id, mod in self.mods.items() if mod.is_active]
    
    def get_mod_status(self, mod_id: str) -> Optional[Dict[str, Any]]:
        """
        Retourne l'état d'un mod
        
        Args:
            mod_id: Identifiant du mod
            
        Returns:
            Dict: État du mod ou None si le mod n'existe pas
        """
        if mod_id not in self.mods:
            return None
            
        return self.mods[mod_id].get_status()
    
    def get_all_mods_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Retourne l'état de tous les mods
        
        Returns:
            Dict: Dictionnaire des états de tous les mods
        """
        return {mod_id: mod.get_status() for mod_id, mod in self.mods.items()}
    
    def _get_system_context(self) -> Dict[str, Any]:
        """
        Crée un contexte système pour les mods
        
        Returns:
            Dict: Contexte avec informations système
        """
        # Cette fonction pourrait être étendue pour collecter plus d'informations
        # comme les processus actifs, l'heure, l'état du système, etc.
        return {
            "timestamp": datetime.now().isoformat(),
            "processes": [],  # À remplir avec la liste des processus actifs
            "is_gaming_activity": False,
            "is_media_activity": False,
            "time_of_day": "day",  # 'day' ou 'night'
        }