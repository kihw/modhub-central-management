"""
Action execution module for ModHub Central automation engine.
Defines action types and execution logic.
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime
import json
import subprocess
import os
import platform

logger = logging.getLogger(__name__)

class ActionRunner:
    """
    Executes different types of actions for the automation engine.
    """
    def __init__(self):
        # Register action handlers
        self._action_handlers = {
            'mod_activation': self._execute_mod_activation,
            'mod_deactivation': self._execute_mod_deactivation,
            'notification': self._execute_notification,
            'system_command': self._execute_system_command,
            'settings_change': self._execute_settings_change,
            'custom': self._execute_custom_action,
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ActionRunner initialized")

    def execute_action(self, action_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> bool:
        """
        Execute a single action.
        
        Args:
            action_type: Type of action to execute
            parameters: Parameters for the action
            context: Optional context data for execution
            
        Returns:
            Whether the action was executed successfully
            
        Raises:
            ValueError: If action type is unknown
        """
        if context is None:
            context = {}
            
        action_type = action_type.lower()
        
        # Get the appropriate handler
        handler = self._action_handlers.get(action_type)
        if not handler:
            self.logger.warning(f"Unknown action type: {action_type}")
            raise ValueError(f"Unknown action type: {action_type}")
            
        # Execute the action
        try:
            result = handler(parameters, context)
            return result
        except Exception as e:
            self.logger.error(f"Error executing {action_type} action: {e}", exc_info=True)
            return False

    def get_available_actions(self) -> List[str]:
        """
        Get a list of available action types.
        
        Returns:
            List of action type names
        """
        return list(self._action_handlers.keys())
        
    def _execute_mod_activation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Activate a mod.
        
        Args:
            parameters: Action parameters
            context: Execution context
            
        Returns:
            Whether the action was executed successfully
        """
        mod_id = parameters.get('mod_id')
        mod_type = parameters.get('mod_type')
        config = parameters.get('config')
        
        if not mod_id and not mod_type:
            self.logger.warning("Mod activation action missing mod_id or mod_type")
            return False
            
        mod_manager = context.get('mod_manager')
        if not mod_manager:
            self.logger.warning("No mod manager available in context")
            return False
            
        try:
            # Use either mod_id or mod_type to activate
            if mod_id:
                success = mod_manager.activate_mod(mod_id, config)
            else:
                success = mod_manager.activate_mod(mod_type, config)
                
            if success:
                self.logger.info(f"Successfully activated mod {mod_id or mod_type}")
            else:
                self.logger.warning(f"Failed to activate mod {mod_id or mod_type}")
                
            return success
        except Exception as e:
            self.logger.error(f"Error activating mod {mod_id or mod_type}: {e}", exc_info=True)
            return False
            
    def _execute_mod_deactivation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Deactivate a mod.
        
        Args:
            parameters: Action parameters
            context: Execution context
            
        Returns:
            Whether the action was executed successfully
        """
        mod_id = parameters.get('mod_id')
        mod_type = parameters.get('mod_type')
        
        if not mod_id and not mod_type:
            self.logger.warning("Mod deactivation action missing mod_id or mod_type")
            return False
            
        mod_manager = context.get('mod_manager')
        if not mod_manager:
            self.logger.warning("No mod manager available in context")
            return False
            
        try:
            # Use either mod_id or mod_type to deactivate
            if mod_id:
                success = mod_manager.deactivate_mod(mod_id)
            else:
                success = mod_manager.deactivate_mod(mod_type)
                
            if success:
                self.logger.info(f"Successfully deactivated mod {mod_id or mod_type}")
            else:
                self.logger.warning(f"Failed to deactivate mod {mod_id or mod_type}")
                
            return success
        except Exception as e:
            self.logger.error(f"Error deactivating mod {mod_id or mod_type}: {e}", exc_info=True)
            return False
        
    def _execute_notification(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Send a notification.
        
        Args:
            parameters: Action parameters
            context: Execution context
            
        Returns:
            Whether the action was executed successfully
        """
        title = parameters.get('title', 'ModHub Central')
        message = parameters.get('message', '')
        level = parameters.get('level', 'info')  # info, warning, error
        
        if not message:
            self.logger.warning("Notification action missing message")
            return False
            
        # Log the notification (for history)
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, f"NOTIFICATION: {title} - {message}")
        
        # In a real implementation, this would use a notification system
        # For now, we'll just log it
        self.logger.info(f"Notification sent: {title} - {message}")
        
        # TODO: Implement actual notification delivery (system tray, toast, etc.)
        
        return True
    
    def _execute_system_command(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Execute a system command.
        
        Args:
            parameters: Action parameters
            context: Execution context
            
        Returns:
            Whether the action was executed successfully
        """
        command = parameters.get('command')
        shell = parameters.get('shell', True)
        timeout = parameters.get('timeout', 30)  # seconds
        
        if not command:
            self.logger.warning("System command action missing command")
            return False
            
        # Security check - prevent dangerous commands
        if self._is_dangerous_command(command):
            self.logger.warning(f"Blocked potentially dangerous command: {command}")
            return False
            
        try:
            # Execute the command
            self.logger.info(f"Executing system command: {command}")
            process = subprocess.run(
                command,
                shell=shell,
                timeout=timeout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode == 0:
                self.logger.info(f"Command executed successfully: {command}")
                return True
            else:
                self.logger.warning(f"Command failed with code {process.returncode}: {command}")
                self.logger.debug(f"Command stderr: {process.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout}s: {command}")
            return False
        except Exception as e:
            self.logger.error(f"Error executing command: {e}", exc_info=True)
            return False
    
    def _is_dangerous_command(self, command: str) -> bool:
        """
        Check if a command appears dangerous.
        
        Args:
            command: Command to check
            
        Returns:
            Whether the command appears dangerous
        """
        # Very basic security check - a real implementation would be more sophisticated
        dangerous_patterns = [
            'rm -rf', 'format', 'mkfs', 'dd if=', 
            'shutdown', 'reboot', 'halt', 
            '> /dev/', '> /etc/', '> /sys/'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in command_lower:
                return True
                
        return False
    
    def _execute_settings_change(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Change a system or application setting.
        
        Args:
            parameters: Action parameters
            context: Execution context
            
        Returns:
            Whether the action was executed successfully
        """
        setting_key = parameters.get('key')
        setting_value = parameters.get('value')
        setting_type = parameters.get('type', 'app')  # app, system
        
        if setting_key is None or setting_value is None:
            self.logger.warning("Settings change action missing key or value")
            return False
            
        # Handle application settings
        if setting_type == 'app':
            # Use database to store setting
            db_session = context.get('db_session')
            if db_session:
                try:
                    from ....db.crud import update_setting
                    update_setting(db_session, setting_key, setting_value)
                    self.logger.info(f"Updated app setting {setting_key} to {setting_value}")
                    return True
                except Exception as e:
                    self.logger.error(f"Error updating app setting: {e}", exc_info=True)
                    return False
            else:
                self.logger.warning("No database session available for settings change")
                return False
                
        # Handle system settings
        elif setting_type == 'system':
            # This would integrate with OS-specific settings APIs
            # For now, log that we would change it
            self.logger.info(f"Would change system setting {setting_key} to {setting_value}")
            
            # TODO: Implement actual system settings changes
            
            # Just return successful for now
            return True
            
        else:
            self.logger.warning(f"Unknown settings type: {setting_type}")
            return False
    
    def _execute_custom_action(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Execute a custom action using provided parameters.
        Useful for special-case actions that don't fit other categories.
        
        Args:
            parameters: Action parameters
            context: Execution context
            
        Returns:
            Whether the action was executed successfully
        """
        # This is a placeholder for custom action logic
        # In a real implementation, this would interpret the parameters
        # and execute based on them.
        action_id = parameters.get('id')
        self.logger.info(f"Executing custom action: {action_id}")
        
        # Default to True for custom actions without specific implementation
        return parameters.get('default_result', True)
