import logging
import time
import threading
import datetime
from typing import List, Dict, Any, Callable, Optional, Set, Tuple

from . import conditions
from . import actions
from ..mods.mod_manager import ModManager

class DummyModel:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 0) 
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.is_active = kwargs.get('is_active', False)
        self.priority = kwargs.get('priority', 0)
        self.last_triggered = kwargs.get('last_triggered', None)
        self.conditions = kwargs.get('conditions', [])
        self.actions = kwargs.get('actions', [])
        for key, value in kwargs.items():
            setattr(self, key, value)

class AutomationRule(DummyModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Condition(DummyModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.condition_type = kwargs.get('condition_type', 'unknown')
        self.parameters = kwargs.get('parameters', {})
        self.logic_operator = kwargs.get('logic_operator', 'AND')

class Action(DummyModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action_type = kwargs.get('action_type', 'unknown')
        self.parameters = kwargs.get('parameters', {})

class AutomationEngine:
    def __init__(self, mod_manager: Optional[ModManager] = None, db_session=None):
        self.mod_manager = mod_manager
        self.db_session = db_session
        self._rules: Dict[int, Dict] = {}
        self._rules_lock = threading.RLock()
        self._processing_thread: Optional[threading.Thread] = None
        self._should_stop = threading.Event()
        self._last_evaluation: Dict[int, datetime.datetime] = {}
        self._condition_evaluator = conditions.ConditionEvaluator()
        self._action_runner = actions.ActionRunner()
        self.logger = logging.getLogger(__name__)

    def start(self, interval: float = 1.0) -> bool:
        if interval <= 0:
            raise ValueError("Interval must be positive")
        with self._rules_lock:
            if self._processing_thread and self._processing_thread.is_alive():
                return False
            self._should_stop.clear()
            self._processing_thread = threading.Thread(
                target=self._process_rules_loop,
                args=(interval,),
                daemon=True
            )
            self._processing_thread.start()
            return True

    def stop(self, timeout: float = 5.0) -> bool:
        if not self._processing_thread or not self._processing_thread.is_alive():
            return False
        self._should_stop.set()
        try:
            self._processing_thread.join(timeout=timeout)
            if not self._processing_thread.is_alive():
                self._processing_thread = None
                return True
            return False
        except Exception:
            return False

    def _process_rules_loop(self, interval: float) -> None:
        while not self._should_stop.is_set():
            try:
                self.evaluate_all_rules()
            except Exception as e:
                self.logger.error(f"Rule processing error: {e}", exc_info=True)
            self._should_stop.wait(interval)

    def register_rule(self, rule: AutomationRule) -> None:
        if not isinstance(rule, AutomationRule):
            raise TypeError("Expected AutomationRule instance")
        with self._rules_lock:
            self._rules[rule.id] = self._convert_rule_to_dict(rule)

    def unregister_rule(self, rule_id: int) -> bool:
        with self._rules_lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                return True
            return False

    def update_rule(self, rule: AutomationRule) -> None:
        if not isinstance(rule, AutomationRule):
            raise TypeError("Expected AutomationRule instance")
        with self._rules_lock:
            self._rules[rule.id] = self._convert_rule_to_dict(rule)

    def evaluate_all_rules(self) -> None:
        with self._rules_lock:
            rules_to_process = sorted(
                self._rules.values(),
                key=lambda r: (-r['priority'], r['id'])
            )

        for rule_data in rules_to_process:
            if not rule_data['is_active']:
                continue
            try:
                if self._evaluate_rule_conditions(rule_data):
                    self._execute_rule_actions(rule_data)
                    self._update_rule_triggered(rule_data['id'])
            except Exception as e:
                self.logger.error(f"Rule evaluation error for rule {rule_data['id']}: {e}", exc_info=True)

    def _evaluate_rule_conditions(self, rule_data: Dict) -> bool:
        conditions_data = rule_data.get('conditions', [])
        if not conditions_data:
            return True

        context = {
            'current_time': datetime.datetime.now(),
            'rule_id': rule_data['id'],
            'mod_manager': self.mod_manager
        }

        or_conditions = [c for c in conditions_data if c.get('logic_operator') == 'OR']
        and_conditions = [c for c in conditions_data if c.get('logic_operator') == 'AND']

        if or_conditions:
            return any(self._evaluate_single_condition(c, context) for c in or_conditions)
        return all(self._evaluate_single_condition(c, context) for c in and_conditions)

    def _evaluate_single_condition(self, condition: Dict, context: Dict) -> bool:
        try:
            return self._condition_evaluator.evaluate_single(
                condition.get('condition_type'),
                condition.get('parameters', {}),
                context
            )
        except Exception as e:
            self.logger.error(f"Condition evaluation error: {e}", exc_info=True)
            return False

    def _execute_rule_actions(self, rule_data: Dict) -> None:
        context = {
            'rule_id': rule_data['id'],
            'mod_manager': self.mod_manager,
            'execution_time': datetime.datetime.now()
        }
        
        for action in rule_data.get('actions', []):
            try:
                self._action_runner.execute_action(
                    action.get('action_type'),
                    action.get('parameters', {}),
                    context
                )
            except Exception as e:
                self.logger.error(f"Action execution error for rule {rule_data['id']}: {e}", exc_info=True)

    def _update_rule_triggered(self, rule_id: int) -> None:
        now = datetime.datetime.now()
        self._last_evaluation[rule_id] = now
        if self.db_session and hasattr(self.db_session, 'update_rule_triggered'):
            try:
                self.db_session.update_rule_triggered(rule_id, now)
            except Exception as e:
                self.logger.error(f"Database update error for rule {rule_id}: {e}", exc_info=True)

    def _convert_rule_to_dict(self, rule: AutomationRule) -> Dict:
        return {
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'priority': rule.priority,
            'is_active': rule.is_active,
            'last_triggered': rule.last_triggered,
            'conditions': [{
                'id': c.id,
                'condition_type': getattr(c, 'condition_type', 'unknown'),
                'parameters': getattr(c, 'parameters', {}),
                'logic_operator': getattr(c, 'logic_operator', 'AND')
            } for c in rule.conditions],
            'actions': [{
                'id': a.id,
                'action_type': getattr(a, 'action_type', 'unknown'),
                'parameters': getattr(a, 'parameters', {})
            } for a in rule.actions]
        }

    def get_available_conditions(self) -> List[str]:
        return self._condition_evaluator.get_available_conditions()

    def get_available_actions(self) -> List[str]:
        return self._action_runner.get_available_actions()

    def get_rule_status(self, rule_id: int) -> Dict:
        with self._rules_lock:
            rule_data = self._rules.get(rule_id)
            if not rule_data:
                return {'error': 'Rule not found'}
            last_triggered = self._last_evaluation.get(rule_id)
            return {
                'id': rule_id,
                'name': rule_data['name'],
                'is_active': rule_data['is_active'],
                'last_triggered': last_triggered.isoformat() if last_triggered else None,
                'conditions_count': len(rule_data['conditions']),
                'actions_count': len(rule_data['actions'])
            }