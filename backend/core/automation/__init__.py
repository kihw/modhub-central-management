import time
import psutil
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time as dt_time
from enum import Enum, auto
from dataclasses import dataclass

class ModType(Enum):
    GAMING = auto()
    NIGHT = auto()
    MEDIA = auto()
    CUSTOM = auto()

@dataclass
class Rule:
    conditions: Dict
    actions: List[str]
    priority: int = 0
    is_active: bool = False

    def __post_init__(self):
        self.conditions = self.conditions.copy()
        self.actions = self.actions.copy()
        self.priority = max(0, self.priority)

class ModManager:
    def __init__(self, check_interval: float = 5.0):
        self.active_mods: Dict[str, bool] = {}
        self.rules: List[Rule] = []
        self.process_cache: Dict[str, Tuple[bool, float]] = {}
        self.last_check: float = time.time()
        self.check_interval: float = max(1.0, check_interval)
        
    def add_rule(self, rule: Rule) -> None:
        if not any(r.conditions == rule.conditions and r.actions == rule.actions for r in self.rules):
            self.rules.append(rule)
            self.rules.sort(key=lambda x: x.priority, reverse=True)
    
    def remove_rule(self, rule: Rule) -> bool:
        try:
            self.rules.remove(rule)
            return True
        except ValueError:
            return False
    
    def check_process(self, process_name: str) -> bool:
        current_time = time.time()
        if process_name in self.process_cache:
            cached_result, cache_time = self.process_cache[process_name]
            if current_time - cache_time <= self.check_interval:
                return cached_result

        process_name = process_name.lower()
        is_running = any(
            proc.info['name'].lower() == process_name
            for proc in psutil.process_iter(['name'], ad_value='')
            if self._safe_process_check(proc)
        )
        
        self.process_cache[process_name] = (is_running, current_time)
        return is_running

    @staticmethod
    def _safe_process_check(proc) -> bool:
        try:
            return bool(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def check_time_condition(self, start_time: dt_time, end_time: dt_time) -> bool:
        current_time = datetime.now().time()
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        return current_time >= start_time or current_time <= end_time

    def evaluate_conditions(self, conditions: Dict) -> bool:
        condition_checks = {
            "process": lambda v: self.check_process(v),
            "time_range": lambda v: self.check_time_condition(v["start"], v["end"]),
            "system_idle": lambda v: psutil.cpu_percent(interval=0.1) <= v
        }
        
        return all(
            condition_checks.get(cond_type, lambda _: False)(value)
            for cond_type, value in conditions.items()
        )

    def execute_actions(self, actions: List[str]) -> None:
        for action in actions:
            try:
                action_type, mod_name = action.split(":", 1)
                if action_type in ("enable_mod", "disable_mod"):
                    self.active_mods[mod_name] = action_type == "enable_mod"
            except ValueError:
                logging.error(f"Invalid action format: {action}")
            except Exception as e:
                logging.error(f"Failed to execute action {action}: {str(e)}")

    def update(self) -> None:
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self.process_cache.clear()
            self.last_check = current_time
            
        for rule in self.rules:
            is_valid = self.evaluate_conditions(rule.conditions)
            if is_valid != rule.is_active:
                rule.is_active = is_valid
                if is_valid:
                    self.execute_actions(rule.actions)

    def get_active_mods(self) -> List[str]:
        return [mod for mod, active in self.active_mods.items() if active]

    def reset(self) -> None:
        self.active_mods.clear()
        self.process_cache.clear()
        self.rules.clear()
        self.last_check = time.time()