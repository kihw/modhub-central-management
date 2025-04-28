from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Any, Optional
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime

class ModState(Enum):
    """
    Représente les différents états possibles d'un mod
    """
    INACTIVE = auto()
    ACTIVE = auto()
    ERROR = auto()
    PAUSED = auto()
    INITIALIZING = auto()

@dataclass
class ModMetadata:
    """
    Métadonnées complètes pour un mod
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ''
    description: Optional[str] = None
    version: str = '0.1.0'
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activated: Optional[datetime] = None
    total_activation_time: int = 0  # en secondes
    activation_count: int = 0

class ModBase(ABC):
    """
    Classe de base abstraite définissant le comportement et les propriétés 
    fondamentales de tous les mods.
    """
    def __init__(
        self, 
        name: str, 
        description: Optional[str] = None,
        priority: int = 50
    ):
        """
        Initialise un mod avec ses propriétés de base
        
        Args:
            name (str): Nom du mod
            description (str, optional): Description détaillée
            priority (int, optional): Priorité du mod (0-100)
        """
        self._metadata = ModMetadata(
            name=name, 
            description=description
        )
        
        self._state = ModState.INACTIVE
        self._priority = max(0, min(100, priority))
        
        # Configuration du logging
        self._logger = logging.getLogger(f'mod.{name}')
        
        # Configuration du mod
        self._config: Dict[str, Any] = {}
        
        # Timestamps pour le tracking
        self._activation_start: Optional[datetime] = None

    @property
    def metadata(self) -> ModMetadata:
        """
        Obtenir les métadonnées du mod
        
        Returns:
            ModMetadata: Métadonnées du mod
        """
        return self._metadata

    @property
    def state(self) -> ModState:
        """
        Obtenir l'état actuel du mod
        
        Returns:
            ModState: État du mod
        """
        return self._state

    @property
    def priority(self) -> int:
        """
        Obtenir la priorité du mod
        
        Returns:
            int: Priorité du mod
        """
        return self._priority

    def update_config(self, config: Dict[str, Any]):
        """
        Mettre à jour la configuration du mod
        
        Args:
            config (Dict[str, Any]): Nouvelle configuration
        """
        self._config.update(config)
        self._logger.info(f"Configuration mise à jour : {config}")

    @abstractmethod
    def activate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Activer le mod
        
        Args:
            context (dict, optional): Contexte d'activation
        
        Returns:
            bool: True si l'activation a réussi, False sinon
        """
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """
        Désactiver le mod
        
        Returns:
            bool: True si la désactivation a réussi, False sinon
        """
        pass

    def _update_activation_metrics(self, success: bool):
        """
        Mettre à jour les métriques d'activation
        
        Args:
            success (bool): Indique si l'activation/désactivation a réussi
        """
        current_time = datetime.now()
        
        if success and self._state == ModState.ACTIVE:
            self._metadata.activation_count += 1
            self._metadata.last_activated = current_time
            
            if self._activation_start:
                duration = (current_time - self._activation_start).total_seconds()
                self._metadata.total_activation_time += int(duration)
        
        # Réinitialiser le timestamp de démarrage
        self._activation_start = current_time if success else None

    def _log_state_change(self, old_state: ModState, new_state: ModState):
        """
        Journaliser les changements d'état
        
        Args:
            old_state (ModState): État précédent
            new_state (ModState): Nouvel état
        """
        self._logger.info(f"Changement d'état : {old_state.name} -> {new_state.name}")

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Valider la configuration du mod
        
        Args:
            config (Dict[str, Any]): Configuration à valider
        
        Returns:
            bool: True si la configuration est valide, False sinon
        """
        # Implémentation de base - à surcharger par les mods spécifiques
        return isinstance(config, dict)