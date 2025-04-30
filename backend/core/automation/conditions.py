import logging
import re
import operator
from datetime import datetime, time
from typing import Dict, Any, List, Optional, Callable

import psutil

logger = logging.getLogger(__name__)

class ConditionEvaluator:
    def __init__(self):
        self._condition_handlers = {
            'process': self._evaluate_process_condition,
            'time': self._evaluate_time_condition,
            'day_of_week': self._evaluate_day_of_week_condition,
            'idle': self._evaluate_idle_condition,
            'resource': self._evaluate_resource_condition,
            'custom': self._evaluate_custom_condition,
        }
        
        self._operators = {
            'eq': operator.eq,
            'neq': operator.ne,
            'gt': operator.gt,
            'gte': operator.ge,
            'lt': operator.lt,
            'lte': operator.le,
            'contains': lambda a, b: b in a if isinstance(a, (str, list)) and b else False,
            'not_contains': lambda a, b: b not in a if isinstance(a, (str, list)) and b else True,
            'matches': lambda a, b: bool(re.search(b, str(a))) if a and b else False,
            'in': lambda a, b: a in b if isinstance(b, (list, set, tuple)) and a else False,
            'not_in': lambda a, b: a not in b if isinstance(b, (list, set, tuple)) and a else True,
        }

    def evaluate_single(self, condition_type: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        context = context or {}
        condition_type = condition_type.lower().strip()
        
        handler = self._condition_handlers.get(condition_type)
        if not handler:
            logger.warning(f"Unknown condition type: {condition_type}")
            return False
            
        try:
            return handler(parameters, context)
        except Exception as e:
            logger.error(f"Error evaluating {condition_type} condition: {str(e)}", exc_info=True)
            return False

    def get_available_conditions(self) -> List[str]:
        return list(self._condition_handlers.keys())

    def _evaluate_process_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        processes = parameters.get('processes', [])
        process_name = parameters.get('process')
        match_type = parameters.get('match_type', 'exact').lower()
        case_sensitive = bool(parameters.get('case_sensitive', False))
        
        if not processes and not process_name:
            return False
        
        if processes:
            any_all = parameters.get('any_all', 'any').lower()
            process_check = any if any_all == 'any' else all
            return process_check(self._is_process_running(p, match_type, case_sensitive) for p in processes)
        
        return self._is_process_running(process_name, match_type, case_sensitive)

    def _is_process_running(self, process_name: str, match_type: str = 'exact', case_sensitive: bool = False) -> bool:
        if not process_name:
            return False
            
        if not case_sensitive:
            process_name = process_name.lower()
            
        for proc in psutil.process_iter(['name'], ad_value=''):
            try:
                current_name = proc.info['name']
                if not current_name:
                    continue
                    
                if not case_sensitive:
                    current_name = current_name.lower()
                    
                if match_type == 'exact' and current_name == process_name:
                    return True
                elif match_type == 'contains' and process_name in current_name:
                    return True
                elif match_type == 'regex' and re.search(process_name, current_name):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return False

    def _evaluate_time_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        current_time = context.get('current_time', datetime.now()).time()
        start_time_str = parameters.get('start_time', '')
        end_time_str = parameters.get('end_time', '')
        operation = parameters.get('operation', 'between').lower()

        try:
            if operation != 'between' and not start_time_str:
                return False

            start_time = datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None

            if operation == 'at' and start_time:
                current_minutes = current_time.hour * 60 + current_time.minute
                target_minutes = start_time.hour * 60 + start_time.minute
                return abs(current_minutes - target_minutes) <= 1

            if operation in ('before', 'after') and start_time:
                return current_time < start_time if operation == 'before' else current_time > start_time

            if operation == 'between' and start_time and end_time:
                if start_time <= end_time:
                    return start_time <= current_time <= end_time
                return current_time >= start_time or current_time <= end_time

        except ValueError as e:
            logger.error(f"Error in time condition: {str(e)}")
            
        return False

    def _evaluate_day_of_week_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        current_date = context.get('current_time', datetime.now())
        current_day = current_date.strftime('%A').lower()
        current_day_num = current_date.weekday()
        
        days = parameters.get('days', [])
        if not days:
            return False
            
        days = [day.lower() if isinstance(day, str) else day for day in days]
        return any(day == current_day if isinstance(day, str) else day == current_day_num for day in days)

    def _evaluate_idle_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        threshold_minutes = float(parameters.get('threshold_minutes', 5))
        last_activity = context.get('last_activity')
        
        if not last_activity:
            return False
            
        idle_time = (context.get('current_time', datetime.now()) - last_activity).total_seconds() / 60
        return idle_time >= threshold_minutes

    def _evaluate_resource_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        resource_type = parameters.get('type', 'cpu').lower()
        threshold = float(parameters.get('threshold', 80))
        operator_name = parameters.get('operator', 'gt')
        
        compare_op = self._operators.get(operator_name)
        if not compare_op:
            return False

        resource_handlers = {
            'cpu': lambda: psutil.cpu_percent(interval=0.1),
            'memory': lambda: psutil.virtual_memory().percent,
            'disk': lambda: psutil.disk_usage('/').percent
        }
        
        try:
            handler = resource_handlers.get(resource_type)
            if not handler:
                return False
                
            return compare_op(handler(), threshold)
        except Exception as e:
            logger.error(f"Resource monitoring error: {str(e)}")
            return False

    def _evaluate_custom_condition(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        condition_id = parameters.get('id')
        logger.debug(f"Evaluating custom condition: {condition_id}")
        return bool(parameters.get('default_result', True))