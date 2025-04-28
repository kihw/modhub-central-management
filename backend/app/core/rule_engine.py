import json
from typing import List, Dict, Any
import logging
from pydantic import BaseModel
from app.core.db import get_db
from app.models.rule import Rule
from pathlib import Path

logger = logging.getLogger(__name__)

class RuleAction(BaseModel):
    action_type: str  # activate_mod, deactivate_mod, etc.
    target: str       # mod name or other target
    priority: int = 0

class RuleEngine:
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        
    async def load_rules(self):
        """Load rules from database"""
        async with get_db() as db:
            db_rules = await db.query(Rule).all()
            self.rules = [json.loads(rule.definition) for rule in db_rules]
        logger.info(f"Loaded {len(self.rules)} rules")
    
    async def save_rule(self, rule: Dict[str, Any]) -> int:
        """Save a new rule to database"""
        async with get_db() as db:
            db_rule = Rule(
                name=rule.get("name", "Unnamed Rule"),
                description=rule.get("description", ""),
                definition=json.dumps(rule),
                is_active=rule.get("is_active", True)
            )
            db.add(db_rule)
            await db.commit()
            await db.refresh(db_rule)
            return db_rule.id
    
    async def evaluate_rules(self, active_processes: List[str]) -> List[RuleAction]:
        """Evaluate all rules and return actions to perform"""
        actions: List[RuleAction] = []
        
        for rule in self.rules:
            if not rule.get("is_active", True):
                continue
                
            if self._evaluate_conditions(rule.get("conditions", []), active_processes):
                rule_actions = rule.get("actions", [])
                for action in rule_actions:
                    actions.append(RuleAction(
                        action_type=action.get("type"),
                        target=action.get("target"),
                        priority=action.get("priority", 0)
                    ))
        
        # Sort actions by priority
        actions.sort(key=lambda x: x.priority, reverse=True)
        
        # Remove duplicate actions (keep highest priority)
        unique_actions = {}
        for action in actions:
            key = f"{action.action_type}_{action.target}"
            if key not in unique_actions:
                unique_actions[key] = action
        
        return list(unique_actions.values())
    
    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], active_processes: List[str]) -> bool:
        """Evaluate conditions for a rule"""
        if not conditions:
            return False
            
        # Check operator (AND/OR)
        operator = conditions[0].get("operator", "AND").upper()
        
        results = []
        for condition in conditions[1:]:  # Skip operator
            condition_type = condition.get("type")
            
            if condition_type == "process_running":
                process_name = condition.get("process_name")
                is_running = any(process_name.lower() in process.lower() for process in active_processes)
                results.append(is_running)
            
            elif condition_type == "time_range":
                import datetime
                current_time = datetime.datetime.now().time()
                start_time = datetime.time(*map(int, condition.get("start_time").split(":")))
                end_time = datetime.time(*map(int, condition.get("end_time").split(":")))
                
                if start_time <= end_time:
                    is_in_range = start_time <= current_time <= end_time
                else:  # Handle overnight ranges
                    is_in_range = current_time >= start_time or current_time <= end_time
                    
                results.append(is_in_range)
                
            elif condition_type == "custom":
                # Custom conditions can be implemented here
                pass
        
        if operator == "AND":
            return all(results)
        elif operator == "OR":
            return any(results)
        
        return False