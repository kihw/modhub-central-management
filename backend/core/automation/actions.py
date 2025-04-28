"""
Module defining automation actions that can be triggered by rules.
These actions interact with the device control modules to execute commands.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from core.device_control import device_registry
from db.models import Rule, Device, ActionLog

logger = logging.getLogger(__name__)

class ActionRunner:
    """Handles the execution of automation actions"""
    
    @staticmethod
    async def execute_action(action_data: Dict[str, Any], rule_id: Optional[str] = None) -> bool:
        """
        Execute an action based on the provided action data
        
        Args:
            action_data: Dictionary containing action details
            rule_id: Optional ID of the rule that triggered this action
            
        Returns:
            bool: Success status of the action execution
        """
        try:
            action_type = action_data.get("type")
            device_id = action_data.get("device_id")
            parameters = action_data.get("parameters", {})
            
            if not action_type:
                logger.error("Missing action type in action data")
                return False
                
            # Log the action being executed
            logger.info(f"Executing action: {action_type} for device: {device_id} with params: {parameters}")
            
            # Handle different action types
            if action_type == "device_command":
                return await ActionRunner._execute_device_command(device_id, parameters, rule_id)
            elif action_type == "notification":
                return await ActionRunner._send_notification(parameters, rule_id)
            elif action_type == "scene_activation":
                return await ActionRunner._activate_scene(parameters, rule_id)
            else:
                logger.error(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.exception(f"Error executing action: {str(e)}")
            return False
    
    @staticmethod
    async def _execute_device_command(device_id: str, parameters: Dict[str, Any], rule_id: Optional[str]) -> bool:
        """Execute a command on a specific device"""
        if not device_id:
            logger.error("Missing device_id for device_command action")
            return False
            
        device_controller = device_registry.get_controller(device_id)
        if not device_controller:
            logger.error(f"No controller found for device ID: {device_id}")
            return False
            
        command = parameters.get("command")
        if not command:
            logger.error("Missing command in parameters")
            return False
            
        command_params = parameters.get("command_parameters", {})
        success = await device_controller.execute_command(command, command_params)
        
        # Log the action result
        await ActionRunner._log_action(
            action_type="device_command",
            device_id=device_id,
            parameters=parameters,
            rule_id=rule_id,
            success=success
        )
        
        return success
    
    @staticmethod
    async def _send_notification(parameters: Dict[str, Any], rule_id: Optional[str]) -> bool:
        """Send a notification based on parameters"""
        message = parameters.get("message", "")
        channel = parameters.get("channel", "app")
        priority = parameters.get("priority", "normal")
        
        # Implementation would depend on notification channels available
        # For now, we just log it
        logger.info(f"Notification ({channel}, {priority}): {message}")
        
        # Log the action
        await ActionRunner._log_action(
            action_type="notification",
            parameters=parameters,
            rule_id=rule_id,
            success=True
        )
        
        return True
    
    @staticmethod
    async def _activate_scene(parameters: Dict[str, Any], rule_id: Optional[str]) -> bool:
        """Activate a predefined scene (group of actions)"""
        scene_id = parameters.get("scene_id")
        if not scene_id:
            logger.error("Missing scene_id for scene_activation action")
            return False
            
        # Scene activation would involve looking up the scene and executing
        # its defined actions - implementation would depend on how scenes are stored
        logger.info(f"Activating scene: {scene_id}")
        
        # Log the action
        await ActionRunner._log_action(
            action_type="scene_activation",
            parameters=parameters,
            rule_id=rule_id,
            success=True
        )
        
        return True
    
    @staticmethod
    async def _log_action(
        action_type: str,
        parameters: Dict[str, Any],
        success: bool,
        rule_id: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> None:
        """Log an action to the database"""
        # This would typically save to the database
        # For now, just logging to console
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "action_type": action_type,
            "parameters": parameters,
            "success": success,
            "rule_id": rule_id,
            "device_id": device_id
        }
        logger.debug(f"Action log: {log_entry}")
        
        # Actual implementation would save to database
        # await ActionLog.create(**log_entry)