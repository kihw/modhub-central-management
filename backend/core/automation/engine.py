import logging
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
from datetime import datetime

from .conditions import ConditionEvaluator
from .actions import ActionExecutor
from ..device_control import DeviceController
from ...db import crud, models

logger = logging.getLogger(__name__)

class AutomationEngine:
    """
    Main automation engine that processes rules and executes actions
    based on conditions.
    """
    def __init__(self, db_session, device_controller: DeviceController = None):
        self.db_session = db_session
        self.device_controller = device_controller or DeviceController()
        self.condition_evaluator = ConditionEvaluator()
        self.action_executor = ActionExecutor(self.device_controller)
        self.running = False
        self.rules_cache = {}
        self.last_refresh = None
        self.refresh_interval = 60  # seconds

    async def start(self):
        """Start the automation engine"""
        self.running = True
        await self.refresh_rules()
        asyncio.create_task(self._run_engine())
        logger.info("Automation engine started")

    async def stop(self):
        """Stop the automation engine"""
        self.running = False
        logger.info("Automation engine stopped")

    async def refresh_rules(self):
        """Reload rules from database"""
        try:
            rules = await crud.get_all_rules(self.db_session)
            self.rules_cache = {rule.id: rule for rule in rules}
            self.last_refresh = datetime.now()
            logger.info(f"Refreshed {len(rules)} rules")
        except Exception as e:
            logger.error(f"Error refreshing rules: {str(e)}")

    async def _run_engine(self):
        """Main loop that evaluates rules and executes actions"""
        while self.running:
            try:
                # Refresh rules if needed
                now = datetime.now()
                if (self.last_refresh is None or 
                    (now - self.last_refresh).total_seconds() > self.refresh_interval):
                    await self.refresh_rules()
                
                # Process each rule
                for rule_id, rule in self.rules_cache.items():
                    if not rule.enabled:
                        continue
                    
                    should_execute = await self.condition_evaluator.evaluate(
                        rule.conditions, self.device_controller, self.db_session
                    )
                    
                    if should_execute:
                        logger.info(f"Rule '{rule.name}' conditions met, executing actions")
                        
                        # Execute actions
                        for action in rule.actions:
                            try:
                                await self.action_executor.execute(action)
                                
                                # Log execution
                                await crud.create_log(
                                    self.db_session,
                                    models.Log(
                                        rule_id=rule_id,
                                        timestamp=datetime.now(),
                                        message=f"Executed action: {action.action_type}",
                                        level="INFO"
                                    )
                                )
                            except Exception as e:
                                error_msg = f"Error executing action: {str(e)}"
                                logger.error(error_msg)
                                await crud.create_log(
                                    self.db_session,
                                    models.Log(
                                        rule_id=rule_id,
                                        timestamp=datetime.now(),
                                        message=error_msg,
                                        level="ERROR"
                                    )
                                )
            
            except Exception as e:
                logger.error(f"Error in automation engine: {str(e)}")
            
            # Check rules every second
            await asyncio.sleep(1)

    async def test_rule(self, rule_id: int) -> Dict[str, Any]:
        """
        Test a rule's conditions without executing actions
        Returns result details
        """
        rule = await crud.get_rule(self.db_session, rule_id)
        if not rule:
            raise ValueError(f"Rule with ID {rule_id} not found")
        
        result = {
            "rule_id": rule_id,
            "rule_name": rule.name,
            "conditions_met": False,
            "condition_results": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for condition in rule.conditions:
            condition_result = await self.condition_evaluator.evaluate_single(
                condition, self.device_controller, self.db_session
            )
            result["condition_results"].append({
                "condition": condition.dict(),
                "result": condition_result
            })
        
        result["conditions_met"] = all(r["result"] for r in result["condition_results"])
        return result