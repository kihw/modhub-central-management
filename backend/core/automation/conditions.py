"""
Condition evaluation module for ModHub Central automation engine.
Defines condition types and evaluation logic.
"""

import logging
import re
import operator
from datetime import datetime, time
from typing import Dict, Any, Optional, List, Callable, Tuple

# Import system utilities
import psutil

logger = logging.getLogger(__name__)

class ConditionEvaluator:
    """
    Evaluates different types of conditions for the automation engine.
    """
    def __init__(self):
        # Register condition handlers
        self._condition_handlers = {
            'process': self._evaluate_process_condition,
            'time': self._evaluate_time_condition,
            'day_of_week': self._evaluate_day_of_week_condition,
            'idle': self._evaluate_idle_condition,
            'resource': self._evaluate_resource_condition,
            'custom': self._evaluate_custom_condition,
        }
        
        # Operators for comparisons
        self._operators = {
            'eq': operator.eq,
            'neq': operator.ne,
            'gt': operator.gt,
            'gte': operator.ge,
            'lt': operator.lt,
            'lte': operator.le,
            'contains': lambda a, b: b in a,
            'not_contains': lambda a, b: b not in a,
            'matches': lambda a, b: bool(re.search(b, a)),
            'in': lambda a, b: a in b,
            'not_in': lambda a, b: a not in b,
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ConditionEvaluator initialized")

    def evaluate_single(self, condition_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> bool:
        """
        Evaluate a single condition.
        
        Args:
            condition_type: Type of condition to evaluate
            parameters: Parameters for the condition
            context: Optional context data for evaluation
            
        Returns:
            Whether the condition is met
            
        Raises:
            ValueError: If condition type is unknown
        """
        if context is None:
            context = {}
            
        condition_type = condition_type.lower()
        
        # Get the appropriate handler
        handler = self._condition_handlers.get(condition_type)
        if not handler:
            self.logger.warning(f"Unknown condition type: {condition_type}")
            raise ValueError(f"Unknown condition type: {condition_type}")
            
        # Evaluate the condition
        try:
            result = handler(parameters, context)
            return result
        except Exception as e:
            self.logger.error(f"Error evaluating {condition_type} condition: {e}", exc_info=True)
            return False

    def get_available_conditions(self) -> List[str]:
        """
        Get a list of available condition types.
        
        Returns:
            List of condition type names
        """
        return list(self._condition_handlers.keys())

    def _evaluate_process_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a process-based condition.
        
        Args:
            parameters: Condition parameters
            context: Evaluation context
            
        Returns:
            Whether the condition is met
        """
        operation = parameters.get('operation', 'running')
        process_name = parameters.get('process')
        match_type = parameters.get('match_type', 'exact')  # exact, contains, regex
        case_sensitive = parameters.get('case_sensitive', False)
        processes = parameters.get('processes', [])
        
        # If processes list is provided, use that instead of single process
        if processes and not process_name:
            # Check if any/all of the processes are running
            any_all = parameters.get('any_all', 'any')  # any, all
            
            if any_all == 'any':
                return any(self._is_process_running(p, match_type, case_sensitive) for p in processes)
            else:  # all
                return all(self._is_process_running(p, match_type, case_sensitive) for p in processes)
        
        # Single process check
        if not process_name:
            self.logger.warning("Process condition missing process name")
            return False
            
        return self._is_process_running(process_name, match_type, case_sensitive)

    def _is_process_running(self, process_name: str, match_type: str = 'exact', case_sensitive: bool = False) -> bool:
        """
        Check if a specific process is running.
        
        Args:
            process_name: Name of the process to check
            match_type: How to match the process name (exact, contains, regex)
            case_sensitive: Whether to match case-sensitively
            
        Returns:
            Whether the process is running
        """
        if not case_sensitive:
            process_name = process_name.lower()
            
        for proc in psutil.process_iter(['name']):
            try:
                current_name = proc.info['name']
                if not case_sensitive:
                    current_name = current_name.lower()
                    
                if match_type == 'exact':
                    if current_name == process_name:
                        return True
                elif match_type == 'contains':
                    if process_name in current_name:
                        return True
                elif match_type == 'regex':
                    if re.search(process_name, current_name):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return False

    def _evaluate_time_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a time-based condition.
        
        Args:
            parameters: Condition parameters
            context: Evaluation context
            
        Returns:
            Whether the condition is met
        """
        current_time = context.get('current_time', datetime.now()).time()
        
        start_time_str = parameters.get('start_time')
        end_time_str = parameters.get('end_time')
        operation = parameters.get('operation', 'between')  # between, before, after, at
        
        # Handle 'at' operation (specific time)
        if operation == 'at':
            if not start_time_str:
                return False
                
            try:
                target_time = datetime.strptime(start_time_str, '%H:%M').time()
                # Allow a small window (1 minute) for 'at' comparison
                target_minutes = target_time.hour * 60 + target_time.minute
                current_minutes = current_time.hour * 60 + current_time.minute
                return abs(target_minutes - current_minutes) <= 1
            except ValueError:
                self.logger.error(f"Invalid time format: {start_time_str}")
                return False
        
        # Handle 'before' operation
        if operation == 'before':
            if not start_time_str:
                return False
                
            try:
                target_time = datetime.strptime(start_time_str, '%H:%M').time()
                return current_time < target_time
            except ValueError:
                self.logger.error(f"Invalid time format: {start_time_str}")
                return False
        
        # Handle 'after' operation
        if operation == 'after':
            if not start_time_str:
                return False
                
            try:
                target_time = datetime.strptime(start_time_str, '%H:%M').time()
                return current_time > target_time
            except ValueError:
                self.logger.error(f"Invalid time format: {start_time_str}")
                return False
        
        # Handle 'between' operation (default)
        if not start_time_str or not end_time_str:
            self.logger.warning("Time condition missing start or end time")
            return False
            
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            # Handle overnight ranges (e.g., 22:00 to 06:00)
            if start_time > end_time:
                return current_time >= start_time or current_time <= end_time
            else:
                return start_time <= current_time <= end_time
        except ValueError as e:
            self.logger.error(f"Error parsing time values: {e}")
            return False

    def _evaluate_day_of_week_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a day-of-week condition.
        
        Args:
            parameters: Condition parameters
            context: Evaluation context
            
        Returns:
            Whether the condition is met
        """
        current_date = context.get('current_time', datetime.now())
        current_day = current_date.strftime('%A').lower()  # Monday, Tuesday, etc.
        current_day_num = current_date.weekday()  # 0=Monday, 6=Sunday
        
        days = parameters.get('days', [])
        if not days:
            return False
            
        # Convert to lowercase for case-insensitive comparison
        days = [day.lower() if isinstance(day, str) else day for day in days]
        
        # Support both string days and numeric days
        for day in days:
            if isinstance(day, str) and day.lower() == current_day:
                return True
            elif isinstance(day, int) and day == current_day_num:
                return True
                
        return False

    def _evaluate_idle_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate an idle/inactivity condition.
        
        Args:
            parameters: Condition parameters
            context: Evaluation context
            
        Returns:
            Whether the condition is met
        """
        # Get idle threshold in minutes
        threshold_minutes = parameters.get('threshold_minutes', 5)
        
        # In a real implementation, you would get the actual system idle time
        # For now, we'll use a placeholder based on the last_activity value in context
        last_activity = context.get('last_activity')
        
        if not last_activity:
            return False
            
        current_time = context.get('current_time', datetime.now())
        idle_time = (current_time - last_activity).total_seconds() / 60
        
        return idle_time >= threshold_minutes

    def _evaluate_resource_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a system resource condition (CPU, memory, etc.)
        
        Args:
            parameters: Condition parameters
            context: Evaluation context
            
        Returns:
            Whether the condition is met
        """
        resource_type = parameters.get('type', 'cpu')  # cpu, memory, disk
        threshold = parameters.get('threshold', 80)  # percentage
        operator_name = parameters.get('operator', 'gt')  # gt, lt, gte, lte, eq
        
        # Get appropriate comparison operator
        compare_op = self._operators.get(operator_name, operator.gt)
        
        # Get current resource usage
        if resource_type == 'cpu':
            current_value = psutil.cpu_percent()
        elif resource_type == 'memory':
            current_value = psutil.virtual_memory().percent
        elif resource_type == 'disk':
            # Use root disk by default, could be parameterized
            current_value = psutil.disk_usage('/').percent
        else:
            self.logger.warning(f"Unknown resource type: {resource_type}")
            return False
            
        return compare_op(current_value, threshold)

    def _evaluate_custom_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a custom condition using provided parameters.
        Useful for special-case conditions that don't fit other categories.
        
        Args:
            parameters: Condition parameters
            context: Evaluation context
            
        Returns:
            Whether the condition is met
        """
        # This is a placeholder for custom condition logic
        # In a real implementation, this would interpret the parameters
        # and evaluate based on them.
        condition_id = parameters.get('id')
        self.logger.info(f"Evaluating custom condition: {condition_id}")
        
        # Default to True for custom conditions without specific implementation
        return parameters.get('default_result', True)
