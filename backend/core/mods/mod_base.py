from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

class ModBase(ABC):
    """Classe de base abstraite pour tous les types de mods."""
    
    def __init__(self, name: str, description: str, priority: int = 0):
        """
        Initialise un mod avec ses propriétés de base.
        
        Args:
            name: Nom du mod
            description: Description du mod
            priority: Priorité du mod (plus la valeur est élevée, plus le mod est prioritaire)
        """
        self.name = name
        self.description = description
        self.priority = priority
        self.is_active = False
        self.settings = {}
        self.logger = logging.getLogger(f"mod.{name}")
    
    @abstractmethod
    def activate(self, context: Dict[str, Any] = None) -> bool:
        """
        Active le mod avec le contexte actuel.
        
        Args:
            context: Dictionnaire contenant le contexte du système
            
        Returns:
            bool: True si l'activation a réussi, False sinon
        """
        pass
    
    @abstractmethod
    def deactivate(self) -> bool:
        """
        Désactive le mod.
        
        Returns:
            bool: True si la désactivation a réussi, False sinon
        """
        pass
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Met à jour les paramètres du mod.
        
        Args:
            settings: Dictionnaire de paramètres à mettre à jour
        """
        self.settings.update(settings)
        self.logger.info(f"Paramètres mis à jour pour {self.name}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retourne l'état actuel du mod.
        
        Returns:
            Dict: État du mod avec ses propriétés
        """
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "priority": self.priority,
            "settings": self.settings
        }
    
    def __str__(self) -> str:
        """Représentation textuelle du mod."""
        status = "actif" if self.is_active else "inactif"
        return f"{self.name} ({status}) - Priorité: {self.priority}"