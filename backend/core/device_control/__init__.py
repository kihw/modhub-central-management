"""
Device control module for interfacing with various connected devices.
This package contains controllers for different device types and a registry
to manage and access these controllers.
"""
from typing import Dict, Any, Optional, List, Type
import logging
import importlib
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class DeviceController:
    """Base class for all device controllers"""
    
    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        self.device_id = device_id
        self.device_config = device_config
        self.device_type = device_config.get("type", "unknown")
        self.name = device_config.get("name", f"Device {device_id}")
        self.connected = False
        
    async def connect(self) -> bool:
        """
        Connect to the device
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        raise NotImplementedError("Device controllers must implement connect()")
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the device
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        raise NotImplementedError("Device controllers must implement disconnect()")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the device
        
        Returns:
            Dict[str, Any]: Device status data
        """
        raise NotImplementedError("Device controllers must implement get_status()")
    
    async def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Execute a command on the device
        
        Args:
            command: The command to execute
            parameters: Additional parameters for the command
            
        Returns:
            bool: True if command executed successfully, False otherwise
        """
        raise NotImplementedError("Device controllers must implement execute_command()")
    
    @property
    def capabilities(self) -> List[str]:
        """
        Get the capabilities of this device
        
        Returns:
            List[str]: List of capability identifiers
        """
        return self.device_config.get("capabilities", [])


class DeviceRegistry:
    """Registry for managing device controllers"""
    
    def __init__(self):
        self._controllers: Dict[str, DeviceController] = {}
        self._controller_classes: Dict[str, Type[DeviceController]] = {}
        
    def register_controller_class(self, device_type: str, controller_class: Type[DeviceController]) -> None:
        """
        Register a controller class for a specific device type
        
        Args:
            device_type: The type of device this controller handles
            controller_class: The controller class
        """
        self._controller_classes[device_type] = controller_class
        logger.info(f"Registered controller class for device type: {device_type}")
    
    async def load_devices(self, config_path: str = "data/config.json") -> None:
        """
        Load devices from configuration file
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            # Load configurations
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Config file not found: {config_path}")
                return
                
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            devices = config.get("devices", [])
            logger.info(f"Loading {len(devices)} devices from configuration")
            
            # Initialize controllers for each device
            for device_config in devices:
                device_id = device_config.get("id")
                device_type = device_config.get("type")
                
                if not device_id or not device_type:
                    logger.warning(f"Invalid device configuration: {device_config}")
                    continue
                    
                await self.add_device(device_id, device_config)
                
        except Exception as e:
            logger.exception(f"Error loading devices: {str(e)}")
    
    async def add_device(self, device_id: str, device_config: Dict[str, Any]) -> bool:
        """
        Add a device to the registry
        
        Args:
            device_id: Unique identifier for the device
            device_config: Configuration for the device
            
        Returns:
            bool: True if device added successfully, False otherwise
        """
        try:
            device_type = device_config.get("type")
            
            if not device_type:
                logger.error(f"No device type specified for device: {device_id}")
                return False
                
            # Check if we have a controller for this device type
            controller_class = self._controller_classes.get(device_type)
            
            if not controller_class:
                logger.error(f"No controller class registered for device type: {device_type}")
                return False
                
            # Create and initialize the controller
            controller = controller_class(device_id, device_config)
            
            # Connect to the device
            if device_config.get("auto_connect", True):
                connected = await controller.connect()
                if not connected:
                    logger.warning(f"Failed to connect to device: {device_id}")
            
            # Store the controller
            self._controllers[device_id] = controller
            logger.info(f"Added device: {device_id} ({device_type})")
            
            return True
            
        except Exception as e:
            logger.exception(f"Error adding device {device_id}: {str(e)}")
            return False
    
    async def remove_device(self, device_id: str) -> bool:
        """
        Remove a device from the registry
        
        Args:
            device_id: ID of the device to remove
            
        Returns:
            bool: True if device removed successfully, False otherwise
        """
        if device_id not in self._controllers:
            logger.warning(f"Device not found: {device_id}")
            return False
            
        try:
            # Disconnect the device
            controller = self._controllers[device_id]
            await controller.disconnect()
            
            # Remove from registry
            del self._controllers[device_id]
            logger.info(f"Removed device: {device_id}")
            
            return True
        except Exception as e:
            logger.exception(f"Error removing device {device_id}: {str(e)}")
            return False
    
    def get_controller(self, device_id: str) -> Optional[DeviceController]:
        """
        Get a device controller by ID
        
        Args:
            device_id: ID of the device
            
        Returns:
            Optional[DeviceController]: The device controller or None if not found
        """
        return self._controllers.get(device_id)
    
    def get_all_controllers(self) -> Dict[str, DeviceController]:
        """
        Get all device controllers
        
        Returns:
            Dict[str, DeviceController]: Dictionary of device controllers
        """
        return self._controllers
    
    def get_controllers_by_type(self, device_type: str) -> List[DeviceController]:
        """
        Get all controllers of a specific device type
        
        Args:
            device_type: Type of devices to filter by
            
        Returns:
            List[DeviceController]: List of matching device controllers
        """
        return [
            controller for controller in self._controllers.values()
            if controller.device_type == device_type
        ]
    
    def get_controllers_by_capability(self, capability: str) -> List[DeviceController]:
        """
        Get all controllers that have a specific capability
        
        Args:
            capability: Capability to filter by
            
        Returns:
            List[DeviceController]: List of matching device controllers
        """
        return [
            controller for controller in self._controllers.values()
            if capability in controller.capabilities
        ]


# Create the global device registry
device_registry = DeviceRegistry()

# Import device controllers
def load_device_controllers():
    """Load all device controller modules"""
    try:
        controllers_dir = Path(__file__).parent / "controllers"
        if not controllers_dir.exists():
            logger.warning(f"Controllers directory not found: {controllers_dir}")
            return
            
        # Import all controller modules
        for module_file in controllers_dir.glob("*.py"):
            if module_file.name.startswith("__"):
                continue
                
            module_name = module_file.stem
            try:
                module = importlib.import_module(f"core.device_control.controllers.{module_name}")
                logger.info(f"Loaded controller module: {module_name}")
            except ImportError as e:
                logger.error(f"Error importing controller module {module_name}: {str(e)}")
                
    except Exception as e:
        logger.exception(f"Error loading device controllers: {str(e)}")

# Load controllers when the module is imported
load_device_controllers()