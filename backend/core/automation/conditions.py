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
