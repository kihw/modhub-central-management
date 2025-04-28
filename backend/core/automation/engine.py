import logging
import time
import threading
import psutil
import datetime
from typing import List, Dict, Any, Callable, Optional
from enum import Enum, auto
import inspect

class ConditionType(Enum):
    PROCESS_RUNNING = auto()
    TIME_RANGE = auto()
    SYSTEM_STATE = auto()
    RESOURCE_USAGE = auto()
    CUSTOM = auto()

class ActionType(Enum):
    MOD_ACTIVATION = auto()
    MOD_DEACTIVATION = auto()
    SYSTEM_COMMAND = auto()
    NOTIFICATION = auto()
    CUSTOM = auto()

class SystemStateChecker:
    """
    Utility class for checking various system states
    """
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """
        Check if a specific process is running
        
        Args:
            process_name (str): Name of the process to check
        
        Returns:
            bool: True if process is running, False otherwise
        """
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                return True
        return False
    
    @staticmethod
    def check_resource_usage(resource_type: str, threshold: float) -> bool:
        """
        Check system resource usage
        
        Args:
            resource_type (str): Type of resource (cpu, memory, disk)
            threshold (float): Usage threshold percentage
        
        Returns:
            bool: True if usage is above threshold, False otherwise
        """
        try:
            if resource_type == 'cpu':
                return psutil.cpu_percent() > threshold
            elif resource_type == 'memory':
                return psutil.virtual_memory().percent > threshold
            elif resource_type == 'disk':
                return psutil.disk_usage('/').percent > threshold
            else:
                raise ValueError(f"Unknown resource type: {resource_type}")
        except Exception as e:
            logging.error(f"Error checking resource usage: {e}")
            return False

class AutomationRule:
    """
    Represents a single automation rule with advanced validation and execution
    """
    def __init__(
        self, 
        name: str, 
        conditions: List[Dict[str, Any]], 
        actions: List[Dict[str, Any]],
        priority: int = 5,
        enabled: bool = True
    ):
        self.name = name
        self.conditions = conditions
        self.actions = actions
        self.priority = priority
        self.enabled = enabled
        self.last_executed = None
        self.execution_count = 0
        self.logger = logging.getLogger(__name__)
        
        self._validate_rule()

    def _validate_rule(self):
        """
        Validate the rule's structure and components
        
        Raises:
            ValueError: If rule is improperly configured
        """
        # Validate conditions
        for condition in self.conditions:
            if 'type' not in condition or 'parameters' not in condition:
                raise ValueError(f"Invalid condition in rule {self.name}")
            
            try:
                ConditionType[condition['type'].upper()]
            except KeyError:
                raise ValueError(f"Unknown condition type: {condition['type']}")
        
        # Validate actions
        for action in self.actions:
            if 'type' not in action or 'parameters' not in action:
                raise ValueError(f"Invalid action in rule {self.name}")
            
            try:
                ActionType[action['type'].upper()]
            except KeyError:
                raise ValueError(f"Unknown action type: {action['type']}")

class AutomationEngine:
    """
    Sophisticated automation engine with advanced rule processing
    """
    def __init__(self, mod_manager=None):
        self._rules: List[AutomationRule] = []
        self._condition_checkers: Dict[ConditionType, Callable] = {
            ConditionType.PROCESS_RUNNING: self._check_process_condition,
            ConditionType.TIME_RANGE: self._check_time_condition,
            ConditionType.RESOURCE_USAGE: self._check_resource_condition
        }
        self._action_executors: Dict[ActionType, Callable] = {
            ActionType.MOD_ACTIVATION: self._execute_mod_activation,
            ActionType.MOD_DEACTIVATION: self._execute_mod_deactivation,
            ActionType.NOTIFICATION: self._execute_notification
        }
        self._rule_lock = threading.Lock()
        self._mod_manager = mod_manager
        self.logger = logging.getLogger(__name__)

    def add_rule(self, rule: AutomationRule):
        """
        Add a new automation rule
        
        Args:
            rule (AutomationRule): Rule to add
        """
        with self._rule_lock:
            # Check for duplicate rule names
            if any(existing_rule.name == rule.name for existing_rule in self._rules):
                self.logger.warning(f"Rule {rule.name} already exists. Replacing.")
            
            # Add rule, sorting by priority (descending)
            self._rules.append(rule)
            self._rules.sort(key=lambda r: r.priority, reverse=True)

    def process_rules(self):
        """
        Process all enabled rules
        """
        for rule in self._rules:
            if not rule.enabled:
                continue

            try:
                # Check if all conditions are met
                if self._evaluate_rule_conditions(rule):
                    # Execute rule actions
                    self._execute_rule_actions(rule)
                    
                    # Update rule execution metadata
                    rule.last_executed = time.time()
                    rule.execution_count += 1
            except Exception as e:
                self.logger.error(f"Error processing rule {rule.name}: {e}")

    def _evaluate_rule_conditions(self, rule: AutomationRule) -> bool:
        """
        Evaluate all conditions for a given rule
        
        Args:
            rule (AutomationRule): Rule to evaluate
        
        Returns:
            bool: True if all conditions are met, False otherwise
        """
        for condition in rule.conditions:
            condition_type = ConditionType[condition['type'].upper()]
            
            # Find appropriate condition checker
            condition_checker = self._condition_checkers.get(condition_type)
            if not condition_checker:
                self.logger.warning(f"No checker found for condition type {condition_type}")
                return False
            
            # Check the condition
            if not condition_checker(condition['parameters']):
                return False
        
        return True

    def _execute_rule_actions(self, rule: AutomationRule):
        """
        Execute all actions for a given rule
        
        Args:
            rule (AutomationRule): Rule to execute
        """
        for action in rule.actions:
            action_type = ActionType[action['type'].upper()]
            
            # Find appropriate action executor
            action_executor = self._action_executors.get(action_type)
            if not action_executor:
                self.logger.warning(f"No executor found for action type {action_type}")
                continue
            
            # Execute the action
            action_executor(action['parameters'])

    def _check_process_condition(self, parameters: Dict[str, Any]) -> bool:
        """
        Check if specified processes are running
        
        Args:
            parameters (Dict[str, Any]): Condition parameters
        
        Returns:
            bool: True if condition is met, False otherwise
        """
        process_names = parameters.get('processes', [])
        match_type = parameters.get('match_type', 'any')  # 'any' or 'all'
        
        if match_type == 'any':
            return any(SystemStateChecker.is_process_running(p) for p in process_names)
        else:
            return all(SystemStateChecker.is_process_running(p) for p in process_names)

    def _check_time_condition(self, parameters: Dict[str, Any]) -> bool:
        """
        Check if current time matches specified time range
        
        Args:
            parameters (Dict[str, Any]): Condition parameters
        
        Returns:
            bool: True if condition is met, False otherwise
        """
        now = datetime.datetime.now().time()
        
        start_time_str = parameters.get('start_time')
        end_time_str = parameters.get('end_time')
        
        if not start_time_str or not end_time_str:
            return False
        
        start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
        
        # Handle overnight time ranges
        if start_time > end_time:
            return now >= start_time or now <= end_time
        else:
            return start_time <= now <= end_time

    def _check_resource_condition(self, parameters: Dict[str, Any]) -> bool:
        """
        Check system resource usage
        
        Args:
            parameters (Dict[str, Any]): Condition parameters
        
        Returns:
            bool: True if condition is met, False otherwise
        """
        resource_type = parameters.get('type')
        threshold = parameters.get('threshold', 80)
        
        return SystemStateChecker.check_resource_usage(resource_type, threshold)

    def _execute_mod_activation(self, parameters: Dict[str, Any]):
        """
        Activate a mod
        
        Args:
            parameters (Dict[str, Any]): Action parameters
        """
        if not self._mod_manager:
            self.logger.warning("No mod manager available")
            return
        
        mod_id = parameters.get('mod_id')
        if not mod_id:
            self.logger.warning("No mod ID specified for activation")
            return
        
        self._mod_manager.activate_mod(mod_id)

    def _execute_mod_deactivation(self, parameters: Dict[str, Any]):
        """
        Deactivate a mod
        
        Args:
            parameters (Dict[str, Any]): Action parameters
        """
        if not self._mod_manager:
            self.logger.warning("No mod manager available")
            return
        
        mod_id = parameters.get('mod_id')
        if not mod_id:
            self.logger.warning("No mod ID specified for deactivation")
            return
        
        self._mod_manager.deactivate_mod(mod_id)

    def _execute_notification(self, parameters: Dict[str, Any]):
        """
        Send a notification
        
        Args:
            parameters (Dict[str, Any]): Notification parameters
        """
        message = parameters.get('message', 'No message')
        title = parameters.get('title', 'ModHub Notification')
        
        # In a real application, this would use a notification service
        self.logger.info(f"NOTIFICATION - {title}: {message}")

    def register_custom_condition_checker(self, condition_type: ConditionType, checker: Callable):
        """
        Register a custom condition checker
        
        Args:
            condition_type (ConditionType): Type of condition
            checker (Callable): Function to check the condition
        """
        # Validate checker signature
        sig = inspect.signature(checker)
        if len(sig.parameters) != 1:
            raise ValueError("Condition checker must accept one parameter (dict)")
        
        self._condition_checkers[condition_type] = checker

    def register_custom_action_executor(self, action_type: ActionType, executor: Callable):
        """
        Register a custom action executor
        
        Args:
            action_type (ActionType): Type of action
            executor (Callable): Function to execute the action
        """
        # Validate executor signature
        sig = inspect.signature(executor)
        if len(sig.parameters) != 1:
            raise ValueError("Action executor must accept one parameter (dict)")
        
        self._action_executors[action_type] = executor