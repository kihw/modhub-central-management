from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, time
import logging

class Condition(ABC):
    """Classe de base abstraite pour toutes les conditions d'automatisation."""
    
    def __init__(self, name: str, description: str):
        """
        Initialise une condition avec ses propriétés de base.
        
        Args:
            name: Nom de la condition
            description: Description de la condition
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"automation.condition.{name}")
    
    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Évalue si la condition est remplie dans le contexte donné.
        
        Args:
            context: Dictionnaire contenant le contexte du système
            
        Returns:
            bool: True si la condition est remplie, False sinon
        """
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Retourne les informations de base de la condition."""
        return {
            "name": self.name,
            "description": self.description
        }


class TimeCondition(Condition):
    """Condition basée sur l'heure actuelle."""
    
    def __init__(self, start_time: str, end_time: str):
        """
        Initialise une condition de temps.
        
        Args:
            start_time: Heure de début au format HH:MM
            end_time: Heure de fin au format HH:MM
        """
        super().__init__(
            name="Time Condition",
            description="Vérifie si l'heure actuelle est dans une plage spécifique"
        )
        self.start_time = start_time
        self.end_time = end_time
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Vérifie si l'heure actuelle est dans la plage définie.
        
        Args:
            context: Contexte du système (doit contenir 'current_time' ou utilisera datetime.now())
            
        Returns:
            bool: True si l'heure actuelle est dans la plage définie
        """
        try:
            # Obtenir l'heure actuelle du contexte ou utiliser l'heure du système
            current_time = context.get("current_time", datetime.now().time())
            if isinstance(current_time, datetime):
                current_time = current_time.time()
            
            # Convertir les chaînes d'heure en objets time
            start_hour, start_minute = map(int, self.start_time.split(':'))
            end_hour, end_minute = map(int, self.end_time.split(':'))
            
            start = time(start_hour, start_minute)
            end = time(end_hour, end_minute)
            
            # Si l'heure de fin est avant l'heure de début, cela signifie que la période
            # s'étend sur deux jours (ex: 22:00 à 07:00)
            if end < start:
                return current_time >= start or current_time <= end
            else:
                return start <= current_time <= end
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation de la condition de temps: {e}")
            return False


class ProcessCondition(Condition):
    """Condition basée sur la présence d'un processus spécifique."""
    
    def __init__(self, process_names: List[str], match_any: bool = True):
        """
        Initialise une condition de processus.
        
        Args:
            process_names: Liste des noms de processus à détecter
            match_any: Si True, la condition est remplie si l'un des processus est détecté
                      Si False, tous les processus doivent être détectés
        """
        super().__init__(
            name="Process Condition",
            description="Vérifie si certains processus sont en cours d'exécution"
        )
        self.process_names = [name.lower() for name in process_names]
        self.match_any = match_any
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Vérifie si les processus spécifiés sont en cours d'exécution.
        
        Args:
            context: Contexte du système (doit contenir 'processes')
            
        Returns:
            bool: True si la condition de processus est remplie
        """
        if "processes" not in context:
            self.logger.warning("Impossible d'évaluer la condition: pas de liste de processus dans le contexte")
            return False
        
        processes = context["processes"]
        detected_processes = []
        
        # Vérifier chaque processus dans la liste
        for process_name in self.process_names:
            for proc in processes:
                if process_name in proc.get("name", "").lower():
                    detected_processes.append(process_name)
                    if self.match_any:
                        return True  # Un seul processus trouvé suffit si match_any=True
        
        # Si match_any=False, tous les processus doivent être trouvés
        if not self.match_any:
            return len(detected_processes) == len(self.process_names)
        
        # Si on arrive ici avec match_any=True, aucun processus n'a été trouvé
        return False


class IdleCondition(Condition):
    """Condition basée sur le temps d'inactivité de l'utilisateur."""
    
    def __init__(self, idle_time_minutes: int):
        """
        Initialise une condition d'inactivité.
        
        Args:
            idle_time_minutes: Temps d'inactivité minimum en minutes
        """
        super().__init__(
            name="Idle Condition",
            description=f"Vérifie si l'utilisateur est inactif depuis au moins {idle_time_minutes} minutes"
        )
        self.idle_time_minutes = idle_time_minutes
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Vérifie si l'utilisateur est inactif depuis le temps spécifié.
        
        Args:
            context: Contexte du système (doit contenir 'idle_time_minutes')
            
        Returns:
            bool: True si l'utilisateur est inactif depuis assez longtemps
        """
        if "idle_time_minutes" not in context:
            self.logger.warning("Impossible d'évaluer la condition: pas de temps d'inactivité dans le contexte")
            return False
        
        return context["idle_time_minutes"] >= self.idle_time_minutes


class CompositeCondition(Condition):
    """Condition composée de plusieurs conditions avec opérateur logique (AND/OR)."""
    
    def __init__(self, conditions: List[Condition], operator: str = "AND"):
        """
        Initialise une condition composite.
        
        Args:
            conditions: Liste de conditions
            operator: Opérateur logique ("AND" ou "OR")
        """
        super().__init__(
            name="Composite Condition",
            description=f"Groupe de conditions avec opérateur {operator}"
        )
        self.conditions = conditions
        self.operator = operator.upper()
        if self.operator not in ["AND", "OR"]:
            raise ValueError("L'opérateur doit être 'AND' ou 'OR'")
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Évalue l'ensemble des conditions selon l'opérateur logique.
        
        Args:
            context: Contexte du système
            
        Returns:
            bool: Résultat de l'évaluation des conditions combinées
        """
        if not self.conditions:
            return True  # Une condition vide est toujours vraie
        
        if self.operator == "AND":
            return all(condition.evaluate(context) for condition in self.conditions)
        else:  # OR
            return any(condition.evaluate(context) for condition in self.conditions)


class CustomCondition(Condition):
    """Condition personnalisée basée sur une fonction d'évaluation définie par l'utilisateur."""
    
    def __init__(self, name: str, description: str, evaluate_func: Callable[[Dict[str, Any]], bool]):
        """
        Initialise une condition personnalisée.
        
        Args:
            name: Nom de la condition
            description: Description de la condition
            evaluate_func: Fonction d'évaluation qui prend un contexte et retourne un booléen
        """
        super().__init__(name=name, description=description)
        self.evaluate_func = evaluate_func
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Évalue la condition en utilisant la fonction personnalisée."""
        try:
            return self.evaluate_func(context)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation de la condition personnalisée: {e}")
            return False


# Classe de fabrique pour créer facilement des conditions
class ConditionFactory:
    """Fabrique pour créer des conditions."""
    
    @staticmethod
    def create_time_condition(start_time: str, end_time: str) -> TimeCondition:
        """Crée une condition de temps."""
        return TimeCondition(start_time, end_time)
    
    @staticmethod
    def create_process_condition(process_names: List[str], match_any: bool = True) -> ProcessCondition:
        """Crée une condition de processus."""
        return ProcessCondition(process_names, match_any)
    
    @staticmethod
    def create_idle_condition(idle_time_minutes: int) -> IdleCondition:
        """Crée une condition d'inactivité."""
        return IdleCondition(idle_time_minutes)
    
    @staticmethod
    def create_and_condition(conditions: List[Condition]) -> CompositeCondition:
        """Crée une condition composite avec opérateur AND."""
        return CompositeCondition(conditions, "AND")
    
    @staticmethod
    def create_or_condition(conditions: List[Condition]) -> CompositeCondition:
        """Crée une condition composite avec opérateur OR."""
        return CompositeCondition(conditions, "OR")
    
    @staticmethod
    def create_custom_condition(name: str, description: str, evaluate_func: Callable[[Dict[str, Any]], bool]) -> CustomCondition:
        """Crée une condition personnalisée."""
        return CustomCondition(name, description, evaluate_func)