"""
Automation Engine module for ModHub Central.
Manages rule evaluation, triggering, and action execution.
"""

import logging
import time
import threading
import datetime
from typing import List, Dict, Any, Callable, Optional, Set, Tuple

# Importer localement depuis le même package
from . import conditions
from . import actions

# Importer de façon relative, mais avec le bon niveau
from ..mods.mod_manager import ModManager

# Utilisons des classes fictives pour éviter les importations problématiques
# au lieu de: from ...db.models import AutomationRule, Condition, Action
class DummyModel:
    """Classe fictive pour représenter les modèles de base de données"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = kwargs.get('id', 0)
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.is_active = kwargs.get('is_active', False)
        self.priority = kwargs.get('priority', 0)
        self.last_triggered = kwargs.get('last_triggered', None)
        self.conditions = kwargs.get('conditions', [])
        self.actions = kwargs.get('actions', [])

# Classes fictives pour les modèles de base de données
class AutomationRule(DummyModel):
    """Classe fictive pour AutomationRule"""
    pass

class Condition(DummyModel):
    """Classe fictive pour Condition"""
    pass

class Action(DummyModel):
    """Classe fictive pour Action"""
    pass

logger = logging.getLogger(__name__)

class AutomationEngine:
    """
    Core automation engine that evaluates conditions and executes actions
    based on system state and defined rules.
    """
    def __init__(self, mod_manager: Optional[ModManager] = None, db_session=None):
        self.mod_manager = mod_manager
        self.db_session = db_session
        
        # Internal state
        self._rules: Dict[int, Dict] = {}  # Rule ID -> Rule data
        self._rules_lock = threading.Lock()
        self._processing_thread = None
        self._should_stop = threading.Event()
        self._last_evaluation: Dict[int, datetime.datetime] = {}
        
        # Initialize condition and action handlers
        self._condition_evaluator = conditions.ConditionEvaluator()
        self._action_runner = actions.ActionRunner()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Automation Engine initialized")

    def start(self, interval: float = 1.0):
        """
        Start the automation engine processing loop.
        
        Args:
            interval: Time between rule evaluations in seconds
        """
        if self._processing_thread and self._processing_thread.is_alive():
            self.logger.warning("Automation engine is already running")
            return
            
        self._should_stop.clear()
        self._processing_thread = threading.Thread(
            target=self._process_rules_loop,
            args=(interval,),
            daemon=True
        )
        self._processing_thread.start()
        self.logger.info(f"Automation engine started with {interval}s interval")

    def stop(self):
        """Stop the automation engine processing loop."""
        if not self._processing_thread or not self._processing_thread.is_alive():
            self.logger.warning("Automation engine is not running")
            return
            
        self._should_stop.set()
        self._processing_thread.join(timeout=5.0)
        if self._processing_thread.is_alive():
            self.logger.warning("Failed to stop automation engine cleanly")
        else:
            self.logger.info("Automation engine stopped")
            self._processing_thread = None

    def _process_rules_loop(self, interval: float):
        """
        Main processing loop that evaluates rules periodically.
        
        Args:
            interval: Time between evaluations in seconds
        """
        self.logger.info("Rule processing loop started")
        
        while not self._should_stop.is_set():
            try:
                self.evaluate_all_rules()
            except Exception as e:
                self.logger.error(f"Error in rule processing loop: {e}", exc_info=True)
                
            # Wait for the next interval or until stopped
            self._should_stop.wait(interval)
            
        self.logger.info("Rule processing loop ended")

    def register_rule(self, rule: AutomationRule):
        """
        Register a rule with the engine.
        
        Args:
            rule: Rule to register
        """
        with self._rules_lock:
            rule_data = self._convert_rule_to_dict(rule)
            self._rules[rule.id] = rule_data
            self.logger.info(f"Registered rule: {rule.name} (ID: {rule.id})")

    def unregister_rule(self, rule_id: int):
        """
        Unregister a rule from the engine.
        
        Args:
            rule_id: ID of the rule to unregister
        """
        with self._rules_lock:
            if rule_id in self._rules:
                rule_name = self._rules[rule_id].get('name', 'Unknown')
                del self._rules[rule_id]
                self.logger.info(f"Unregistered rule: {rule_name} (ID: {rule_id})")
            else:
                self.logger.warning(f"Attempted to unregister unknown rule ID: {rule_id}")

    def update_rule(self, rule: AutomationRule):
        """
        Update a registered rule.
        
        Args:
            rule: Updated rule
        """
        with self._rules_lock:
            if rule.id in self._rules:
                rule_data = self._convert_rule_to_dict(rule)
                self._rules[rule.id] = rule_data
                self.logger.info(f"Updated rule: {rule.name} (ID: {rule.id})")
            else:
                self.register_rule(rule)

    def evaluate_all_rules(self):
        """Evaluate all registered rules against current system state."""
        with self._rules_lock:
            # Make a copy of rules to avoid lock during evaluation
            rules_to_process = list(self._rules.values())
            
        # Sort rules by priority (highest first)
        rules_to_process.sort(key=lambda r: r.get('priority', 0), reverse=True)
        
        for rule_data in rules_to_process:
            rule_id = rule_data.get('id')
            
            # Skip inactive rules
            if not rule_data.get('is_active', False):
                continue
                
            try:
                conditions_met = self._evaluate_rule_conditions(rule_data)
                
                if conditions_met:
                    self._execute_rule_actions(rule_data)
                    self._update_rule_triggered(rule_id)
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule_id}: {e}", exc_info=True)

    def _evaluate_rule_conditions(self, rule_data: Dict) -> bool:
        """
        Evaluate all conditions for a rule.
        
        Args:
            rule_data: Rule data dictionary
            
        Returns:
            True if all conditions are met, False otherwise
        """
        rule_id = rule_data.get('id')
        conditions_data = rule_data.get('conditions', [])
        
        if not conditions_data:
            # If no conditions are defined, rule is always triggered
            self.logger.debug(f"Rule {rule_id} has no conditions, automatically met")
            return True
            
        # Track which conditions are met
        all_conditions_met = True
        
        # Local context for condition evaluation
        context = {
            'current_time': datetime.datetime.now(),
            'rule_id': rule_id
        }
        
        # Special handling for different condition combination logic
        # By default, we use AND logic (all conditions must be met)
        for condition in conditions_data:
            condition_type = condition.get('condition_type')
            parameters = condition.get('parameters', {})
            
            # Evaluate the condition
            try:
                condition_met = self._condition_evaluator.evaluate_single(
                    condition_type, 
                    parameters,
                    context
                )
                
                if not condition_met:
                    all_conditions_met = False
                    
                    # If using AND logic and a condition fails, we can stop early
                    logic_op = condition.get('logic_operator', 'AND')
                    if logic_op == 'AND':
                        self.logger.debug(f"Rule {rule_id}: Condition {condition_type} not met, stopping early")
                        break
                else:
                    # If using OR logic and a condition passes, we can stop early
                    logic_op = condition.get('logic_operator', 'AND')
                    if logic_op == 'OR':
                        self.logger.debug(f"Rule {rule_id}: Condition {condition_type} met, OR condition satisfied")
                        all_conditions_met = True
                        break
                        
            except Exception as e:
                self.logger.error(f"Error evaluating condition for rule {rule_id}: {e}", exc_info=True)
                all_conditions_met = False
                break
                
        return all_conditions_met

    def _execute_rule_actions(self, rule_data: Dict):
        """
        Execute all actions for a rule.
        
        Args:
            rule_data: Rule data dictionary
        """
        rule_id = rule_data.get('id')
        actions_data = rule_data.get('actions', [])
        
        if not actions_data:
            self.logger.warning(f"Rule {rule_id} has no actions defined")
            return
            
        for action in actions_data:
            action_type = action.get('action_type')
            parameters = action.get('parameters', {})
            
            try:
                self.logger.info(f"Executing action {action_type} for rule {rule_id}")
                success = self._action_runner.execute_action(
                    action_type,
                    parameters,
                    {
                        'rule_id': rule_id,
                        'mod_manager': self.mod_manager
                    }
                )
                
                if not success:
                    self.logger.warning(f"Action {action_type} for rule {rule_id} failed")
            except Exception as e:
                self.logger.error(f"Error executing action {action_type} for rule {rule_id}: {e}", exc_info=True)
                # Continue with next action even if one fails

    def _update_rule_triggered(self, rule_id: int):
        """
        Update the last triggered timestamp for a rule.
        
        Args:
            rule_id: ID of the triggered rule
        """
        self._last_evaluation[rule_id] = datetime.datetime.now()
        
        # Update in database if session is available
        if self.db_session:
            try:
                # Utilisation d'importations fictives au lieu de from ...db.crud
                self.logger.info(f"Rule {rule_id} triggered at {datetime.datetime.now()}")
                # La mise à jour dans la base de données sera implémentée ultérieurement
            except Exception as e:
                self.logger.error(f"Error updating rule triggered status: {e}", exc_info=True)

    def _convert_rule_to_dict(self, rule: AutomationRule) -> Dict:
        """
        Convert an AutomationRule model to a dictionary for internal use.
        
        Args:
            rule: Rule model to convert
            
        Returns:
            Dictionary representation of the rule
        """
        rule_dict = {
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'priority': rule.priority,
            'is_active': rule.is_active,
            'last_triggered': rule.last_triggered,
            'conditions': [],
            'actions': []
        }
        
        # Add conditions
        for condition in rule.conditions:
            rule_dict['conditions'].append({
                'id': condition.id,
                'condition_type': condition.condition_type if hasattr(condition, 'condition_type') else 'unknown',
                'parameters': condition.parameters if hasattr(condition, 'parameters') else {},
                'logic_operator': condition.logic_operator if hasattr(condition, 'logic_operator') else 'AND'
            })
            
        # Add actions
        for action in rule.actions:
            rule_dict['actions'].append({
                'id': action.id,
                'action_type': action.action_type if hasattr(action, 'action_type') else 'unknown',
                'parameters': action.parameters if hasattr(action, 'parameters') else {}
            })
            
        return rule_dict

    def get_available_conditions(self) -> List[str]:
        """
        Get list of available condition types.
        
        Returns:
            List of condition type names
        """
        return self._condition_evaluator.get_available_conditions()

    def get_available_actions(self) -> List[str]:
        """
        Get list of available action types.
        
        Returns:
            List of action type names
        """
        return self._action_runner.get_available_actions()

    def get_rule_status(self, rule_id: int) -> Dict:
        """
        Get the current status of a rule.
        
        Args:
            rule_id: ID of the rule
            
        Returns:
            Dictionary with rule status information
        """
        with self._rules_lock:
            if rule_id not in self._rules:
                return {'error': 'Rule not found'}
                
            rule_data = self._rules[rule_id]
            last_triggered = self._last_evaluation.get(rule_id)
            
            return {
                'id': rule_id,
                'name': rule_data.get('name'),
                'is_active': rule_data.get('is_active', False),
                'last_triggered': last_triggered.isoformat() if last_triggered else None,
                'conditions_count': len(rule_data.get('conditions', [])),
                'actions_count': len(rule_data.get('actions', []))
            }