<<<<<<< HEAD
import logging
from typing import List, Dict, Any, Union, Optional
from datetime import datetime, time
import re
import json
import operator

from ...db import models

logger = logging.getLogger(__name__)

class ConditionEvaluator:
    """
    Evaluates conditions for automation rules
    """
    def __init__(self):
        # Mapping of operators to their functions
        self.operators = {
            "eq": operator.eq,
            "neq": operator.ne,
            "gt": operator.gt,
            "gte": operator.ge,
            "lt": operator.lt,
            "lte": operator.le,
            "contains": lambda a, b: b in a,
            "not_contains": lambda a, b: b not in a,
            "matches": lambda a, b: bool(re.match(b, a)),
        }

    async def evaluate(self, conditions: List[models.Condition], device_controller, db_session) -> bool:
        """
        Evaluate all conditions for a rule.
        Returns True if all conditions are met, False otherwise.
        """
        if not conditions:
            return True  # If no conditions, always trigger
        
        results = []
        
        for condition in conditions:
            result = await self.evaluate_single(condition, device_controller, db_session)
            results.append(result)
            
            # Early exit for AND logic (if any condition is False)
            if not result and condition.logic_operator == "AND":
                return False
                
            # Early exit for OR logic (if any condition is True)
            if result and condition.logic_operator == "OR":
                return True
                
        # If we're still here, check overall result based on default logic
        if conditions[0].logic_operator == "OR":
            return any(results)
        else:  # Default is AND
            return all(results)

    async def evaluate_single(self, condition: models.Condition, device_controller, db_session) -> bool:
        """Evaluate a single condition"""
        try:
            condition_type = condition.condition_type.lower()
            
            if condition_type == "device_state":
                return await self._evaluate_device_state(condition, device_controller)
            elif condition_type == "time":
                return self._evaluate_time(condition)
            elif condition_type == "day_of_week":
                return self._evaluate_day_of_week(condition)
            elif condition_type == "numeric_value":
                return self._evaluate_numeric(condition)
            elif condition_type == "string_value":
                return self._evaluate_string(condition)
            elif condition_type == "variable":
                return await self._evaluate_variable(condition, db_session)
            else:
                logger.warning(f"Unknown condition type: {condition_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False

    async def _evaluate_device_state(self, condition: models.Condition, device_controller) -> bool:
        """Evaluate a device state condition"""
        device_id = condition.parameters.get("device_id")
        property_name = condition.parameters.get("property")
        expected_value = condition.parameters.get("value")
        operator_name = condition.parameters.get("operator", "eq")
        
        if not all([device_id, property_name, expected_value is not None]):
            logger.warning(f"Missing required parameters for device state condition: {condition.parameters}")
            return False
        
        # Get current device state
        try:
            current_value = await device_controller.get_device_property(device_id, property_name)
            operator_func = self.operators.get(operator_name, operator.eq)
            
            # Convert values to appropriate types
            if isinstance(expected_value, str) and expected_value.lower() in ["true", "false"]:
                expected_value = expected_value.lower() == "true"
                
            if isinstance(current_value, str) and current_value.lower() in ["true", "false"]:
                current_value = current_value.lower() == "true"
                
            # Numeric comparison
            if isinstance(expected_value, (int, float)) or (isinstance(expected_value, str) and expected_value.replace(".", "", 1).isdigit()):
                try:
                    current_value = float(current_value)
                    expected_value = float(expected_value)
                except (ValueError, TypeError):
                    pass
                    
            return operator_func(current_value, expected_value)
            
        except Exception as e:
            logger.error(f"Error getting device state for {device_id}.{property_name}: {str(e)}")
            return False

    def _evaluate_time(self, condition: models.Condition) -> bool:
        """Evaluate a time-based condition"""
        now = datetime.now().time()
        
        start_time_str = condition.parameters.get("start_time")
        end_time_str = condition.parameters.get("end_time")
        
        if not start_time_str:
            logger.warning("Missing start_time parameter for time condition")
            return False
            
        try:
            # Parse times
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            
            # If end_time is provided, check if current time is between start and end
            if end_time_str:
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
                
                # Handle overnight ranges (e.g., 22:00 to 06:00)
                if start_time > end_time:
                    return now >= start_time or now <= end_time
                else:
                    return start_time <= now <= end_time
            else:
                # Just check if current time matches start_time (within the minute)
                return now.hour == start_time.hour and now.minute == start_time.minute
                
        except ValueError as e:
            logger.error(f"Error parsing time values: {str(e)}")
            return False

    def _evaluate_day_of_week(self, condition: models.Condition) -> bool:
        """Evaluate a day-of-week condition"""
        days = condition.parameters.get("days", [])
        if not days:
            return False
            
        today = datetime.now().strftime("%A").lower()
        days = [day.lower() for day in days]
        
        return today in days

    def _evaluate_numeric(self, condition: models.Condition) -> bool:
        """Evaluate a numeric comparison condition"""
        value = condition.parameters.get("value")
        compare_to = condition.parameters.get("compare_to")
        operator_name = condition.parameters.get("operator", "eq")
        
        if value is None or compare_to is None:
            return False
            
        try:
            value = float(value)
            compare_to = float(compare_to)
            operator_func = self.operators.get(operator_name, operator.eq)
            
            return operator_func(value, compare_to)
        except (ValueError, TypeError) as e:
            logger.error(f"Error comparing numeric values: {str(e)}")
            return False

    def _evaluate_string(self, condition: models.Condition) -> bool:
        """Evaluate a string comparison condition"""
        value = condition.parameters.get("value", "")
        compare_to = condition.parameters.get("compare_to", "")
        operator_name = condition.parameters.get("operator", "eq")
        
        if value is None or compare_to is None:
            return False
            
        operator_func = self.operators.get(operator_name, operator.eq)
        
        # Convert to strings to ensure we can compare
        value = str(value)
        compare_to = str(compare_to)
        
        return operator_func(value, compare_to)

    async def _evaluate_variable(self, condition: models.Condition, db_session) -> bool:
        """Evaluate a condition based on a stored variable"""
        from ...db import crud
        
        variable_name = condition.parameters.get("variable_name")
        expected_value = condition.parameters.get("value")
        operator_name = condition.parameters.get("operator", "eq")
        
        if not variable_name or expected_value is None:
            return False
            
        try:
            # Get variable from database
            variable = await crud.get_variable_by_name(db_session, variable_name)
            
            if not variable:
                logger.warning(f"Variable not found: {variable_name}")
                return False
                
            current_value = variable.value
            operator_func = self.operators.get(operator_name, operator.eq)
            
            # Try to parse JSON if variable value looks like JSON
            if isinstance(current_value, str) and current_value.strip().startswith(("{", "[")):
                try:
                    current_value = json.loads(current_value)
                except json.JSONDecodeError:
                    pass
                    
            # Convert values if needed
            if isinstance(expected_value, str) and expected_value.lower() in ["true", "false"]:
                expected_value = expected_value.lower() == "true"
                
            if isinstance(current_value, str) and current_value.lower() in ["true", "false"]:
                current_value = current_value.lower() == "true"
                
            # Numeric comparison
            if isinstance(expected_value, (int, float)) or (isinstance(expected_value, str) and expected_value.replace(".", "", 1).isdigit()):
                try:
                    current_value = float(current_value)
                    expected_value = float(expected_value)
                except (ValueError, TypeError):
                    pass
                    
            return operator_func(current_value, expected_value)
            
        except Exception as e:
            logger.error(f"Error evaluating variable condition: {str(e)}")
            return False
=======
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
>>>>>>> bdb84f715fb0be664761e28acc7f0b8661da8a4a
