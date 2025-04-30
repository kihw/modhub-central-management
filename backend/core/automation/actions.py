import logging
from typing import Dict, Any, List, Optional, Callable
import subprocess
import os
import platform
from datetime import datetime

logger = logging.getLogger(__name__)

class ActionRunner:
    def __init__(self):
        self._action_handlers: Dict[str, Callable] = {
            'mod_activation': self._execute_mod_activation,
            'mod_deactivation': self._execute_mod_deactivation,
            'notification': self._execute_notification,
            'system_command': self._execute_system_command,
            'settings_change': self._execute_settings_change,
            'custom': self._execute_custom_action,
        }
        self._last_execution: Dict[str, datetime] = {}
        self._dangerous_patterns = frozenset([
            'rm -rf', 'format', 'mkfs', 'dd if=', 
            'shutdown', 'reboot', 'halt',
            '> /dev/', '> /etc/', '> /sys/',
            'del /s', 'del /f', 'format c:',
            '> %systemroot%', '> %windir%'
        ])
        self.logger = logger
        self.logger.info("ActionRunner initialized")

    def execute_action(self, action_type: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        if not isinstance(parameters, dict):
            self.logger.error("Parameters must be a dictionary")
            return False
            
        context = context or {}
        action_type = action_type.lower().strip()
        
        handler = self._action_handlers.get(action_type)
        if not handler:
            self.logger.error(f"Unknown action type: {action_type}")
            return False

        try:
            result = handler(parameters, context)
            if result:
                self._last_execution[action_type] = datetime.now()
            return result
        except Exception as e:
            self.logger.error(f"Error executing {action_type} action: {str(e)}", exc_info=True)
            return False

    def get_available_actions(self) -> List[str]:
        return list(self._action_handlers.keys())

    def get_last_execution(self, action_type: str) -> Optional[datetime]:
        return self._last_execution.get(action_type)
        
    def _execute_mod_activation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        mod_id = parameters.get('mod_id')
        mod_type = parameters.get('mod_type')
        config = parameters.get('config', {})
        
        if not (mod_id or mod_type):
            self.logger.error("Mod activation requires mod_id or mod_type")
            return False
            
        mod_manager = context.get('mod_manager')
        if not mod_manager:
            self.logger.error("Mod manager not available")
            return False
            
        try:
            return mod_manager.activate_mod(mod_id or mod_type, config)
        except Exception as e:
            self.logger.error(f"Mod activation failed: {str(e)}")
            return False
            
    def _execute_mod_deactivation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        mod_id = parameters.get('mod_id')
        mod_type = parameters.get('mod_type')
        
        if not (mod_id or mod_type):
            self.logger.error("Mod deactivation requires mod_id or mod_type")
            return False
            
        mod_manager = context.get('mod_manager')
        if not mod_manager:
            self.logger.error("Mod manager not available")
            return False
            
        try:
            return mod_manager.deactivate_mod(mod_id or mod_type)
        except Exception as e:
            self.logger.error(f"Mod deactivation failed: {str(e)}")
            return False
        
    def _execute_notification(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        title = str(parameters.get('title', 'ModHub Central'))
        message = str(parameters.get('message', '')).strip()
        level = str(parameters.get('level', 'info')).upper()
        
        if not message:
            self.logger.error("Notification requires message")
            return False
            
        try:
            log_level = getattr(logging, level, logging.INFO)
            self.logger.log(log_level, f"NOTIFICATION: {title} - {message}")
            return True
        except Exception as e:
            self.logger.error(f"Notification failed: {str(e)}")
            return False
    
    def _execute_system_command(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        command = parameters.get('command')
        shell = bool(parameters.get('shell', True))
        timeout = max(1, int(parameters.get('timeout', 30)))
        
        if not command:
            self.logger.error("System command required")
            return False
            
        if isinstance(command, str) and self._is_dangerous_command(command):
            self.logger.error(f"Dangerous command blocked: {command}")
            return False
            
        try:
            result = subprocess.run(
                command,
                shell=shell,
                timeout=timeout,
                capture_output=True,
                text=True,
                check=False
            )
            if result.stderr:
                self.logger.warning(f"Command stderr: {result.stderr}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Command execution failed: {str(e)}")
            return False
    
    def _is_dangerous_command(self, command: str) -> bool:
        command = command.lower()
        return any(pattern.lower() in command for pattern in self._dangerous_patterns)
    
    def _execute_settings_change(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        setting_key = parameters.get('key')
        setting_value = parameters.get('value')
        setting_type = str(parameters.get('type', 'app')).lower()
        
        if setting_key is None or setting_value is None:
            self.logger.error("Settings change requires key and value")
            return False
            
        try:
            if setting_type == 'app':
                db_session = context.get('db_session')
                if not db_session:
                    self.logger.error("Database session not available")
                    return False
                from db.crud import update_setting
                return update_setting(db_session, setting_key, setting_value)
            elif setting_type == 'system':
                self.logger.info(f"System setting change: {setting_key}={setting_value}")
                return True
            else:
                self.logger.error(f"Invalid settings type: {setting_type}")
                return False
        except Exception as e:
            self.logger.error(f"Settings change failed: {str(e)}")
            return False
    
    def _execute_custom_action(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        action_id = parameters.get('id')
        if not action_id:
            self.logger.error("Custom action requires id")
            return False
            
        handler = parameters.get('handler')
        if not callable(handler):
            self.logger.warning(f"No handler defined for custom action {action_id}")
            return bool(parameters.get('default_result', False))
            
        try:
            return handler(parameters, context)
        except Exception as e:
            self.logger.error(f"Custom action {action_id} failed: {str(e)}")
            return False