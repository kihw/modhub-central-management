"""
Plugin Management System for ModHub Central

Provides a flexible and extensible plugin architecture 
for dynamic module loading and management.
"""

import os
import sys
import importlib
import inspect
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Type, Optional, List, Union

from core.events import EventType, SystemEvent, global_event_manager
from core.sentry import capture_exception

logger = logging.getLogger(__name__)

class PluginBase:
    """
    Base class for all plugins in ModHub Central
    Provides common plugin lifecycle and metadata management
    """
    
    def __init__(self):
        """
        Initialize plugin with base configuration
        """
        self._metadata: Dict[str, Any] = {
            'id': None,
            'name': self.__class__.__name__,
            'version': '0.1.0',
            'description': self.__class__.__doc__ or 'No description provided',
            'author': 'Unknown',
            'dependencies': [],
            'loaded_at': None,
            'enabled': True
        }
    
    @classmethod
    def get_plugin_metadata(cls) -> Dict[str, Any]:
        """
        Retrieve metadata about the plugin
        
        Returns:
            Dictionary with plugin information
        """
        return {
            'name': cls.__name__,
            'module': cls.__module__,
            'description': cls.__doc__ or 'No description provided',
        }
    
    def initialize(self, context: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin with optional context
        
        Args:
            context: Additional configuration or dependencies
        """
        self._metadata['loaded_at'] = datetime.now()
        logger.info(f"Initializing plugin: {self._metadata['name']}")
    
    def shutdown(self):
        """
        Perform cleanup when the plugin is being unloaded
        """
        logger.info(f"Shutting down plugin: {self._metadata['name']}")
    
    def enable(self):
        """Enable the plugin"""
        self._metadata['enabled'] = True
    
    def disable(self):
        """Disable the plugin"""
        self._metadata['enabled'] = False
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get current plugin metadata
        
        Returns:
            Dictionary of plugin metadata
        """
        return self._metadata.copy()

class PluginManager:
    """
    Advanced plugin management system with dependency tracking,
    lifecycle management, and dynamic loading capabilities
    """
    
    def __init__(
        self, 
        plugin_dirs: Optional[List[str]] = None,
        base_plugin_class: Type[PluginBase] = PluginBase
    ):
        """
        Initialize plugin manager
        
        Args:
            plugin_dirs: List of directories to search for plugins
            base_plugin_class: Base class for plugins
        """
        # Plugin directories with default locations
        self._plugin_dirs = plugin_dirs or [
            str(Path(__file__).parent.parent / "plugins"),
            str(Path.home() / ".modhub" / "plugins")
        ]
        
        # Ensure plugin directories exist
        for directory in self._plugin_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Plugin storage
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        
        # Configuration
        self._base_plugin_class = base_plugin_class
        
        # Dependency tracking
        self._plugin_dependencies: Dict[str, List[str]] = {}
    
    def _load_plugin_module(self, module_path: Path) -> Optional[List[Type[PluginBase]]]:
        """
        Load a plugin module and extract plugin classes
        
        Args:
            module_path: Path to the plugin module
        
        Returns:
            List of discovered plugin classes
        """
        try:
            # Add plugin directory to system path temporarily
            sys.path.insert(0, str(module_path.parent))
            
            try:
                # Import the module dynamically
                module_name = module_path.stem
                module = importlib.import_module(module_name)
                
                # Find plugin classes in the module
                discovered_plugins = []
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, self._base_plugin_class) and 
                        obj is not self._base_plugin_class):
                        discovered_plugins.append(obj)
                
                return discovered_plugins
            
            except Exception as e:
                logger.error(f"Error loading plugin module {module_path}: {e}")
                capture_exception(e, f"Plugin module load error: {module_path}")
                return None
            
        finally:
            # Remove temporarily added path
            sys.path.pop(0)
    
    def discover_plugins(self) -> List[Type[PluginBase]]:
        """
        Discover plugins across all configured directories
        
        Returns:
            List of discovered plugin classes
        """
        discovered_plugins = []
        
        for directory in self._plugin_dirs:
            plugin_dir = Path(directory)
            
            # Find Python files that could be plugins
            for file_path in plugin_dir.glob('*.py'):
                if file_path.stem.startswith('__'):
                    continue
                
                module_plugins = self._load_plugin_module(file_path)
                
                if module_plugins:
                    for plugin_class in module_plugins:
                        # Store plugin class
                        self._plugin_classes[plugin_class.__name__] = plugin_class
                        discovered_plugins.append(plugin_class)
        
        return discovered_plugins
    
    def load_plugin(
        self, 
        plugin_class: Union[Type[PluginBase], str], 
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[PluginBase]:
        """
        Load and initialize a specific plugin
        
        Args:
            plugin_class: Plugin class or name to load
            context: Optional initialization context
        
        Returns:
            Initialized plugin instance
        """
        try:
            # Resolve plugin class if string is provided
            if isinstance(plugin_class, str):
                if plugin_class not in self._plugin_classes:
                    raise ValueError(f"Plugin class {plugin_class} not found")
                plugin_class = self._plugin_classes[plugin_class]
            
            # Check if plugin is already loaded
            if plugin_class.__name__ in self._plugins:
                logger.warning(f"Plugin {plugin_class.__name__} already loaded")
                return self._plugins[plugin_class.__name__]
            
            # Instantiate the plugin
            plugin_instance = plugin_class()
            
            # Initialize the plugin
            plugin_instance.initialize(context)
            
            # Store the plugin
            self._plugins[plugin_class.__name__] = plugin_instance
            
            # Emit plugin loaded event
            asyncio.create_task(
                global_event_manager.emit_event(
                    SystemEvent(
                        event_type=EventType.PLUGIN_LOADED,
                        source='plugin_manager',
                        details={
                            'plugin_name': plugin_class.__name__,
                            'metadata': plugin_instance.get_metadata()
                        }
                    )
                )
            )
            
            logger.info(f"Plugin loaded: {plugin_class.__name__}")
            return plugin_instance
        
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_class}: {e}")
            capture_exception(e, f"Plugin load error: {plugin_class}")
            return None
    
    def unload_plugin(self, plugin_name: str):
        """
        Unload a specific plugin
        
        Args:
            plugin_name: Name of the plugin to unload
        """
        if plugin_name in self._plugins:
            try:
                plugin = self._plugins[plugin_name]
                plugin.shutdown()
                del self._plugins[plugin_name]
                
                # Emit plugin unloaded event
                asyncio.create_task(
                    global_event_manager.emit_event(
                        SystemEvent(
                            event_type=EventType.PLUGIN_UNLOADED,
                            source='plugin_manager',
                            details={
                                'plugin_name': plugin_name
                            }
                        )
                    )
                )
                
                logger.info(f"Plugin unloaded: {plugin_name}")
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_name}: {e}")
                capture_exception(e, f"Plugin unload error: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Retrieve a loaded plugin
        
        Args:
            plugin_name: Name of the plugin
        
        Returns:
            Plugin instance or None
        """
        return self._plugins.get(plugin_name)
    
    def list_available_plugins(self) -> List[Dict[str, Any]]:
        """
        List all discovered plugin classes
        
        Returns:
            List of plugin metadata
        """
        return [
            plugin_class.get_plugin_metadata() 
            for plugin_class in self._plugin_classes.values()
        ]
    
    def load_all_plugins(
        self, 
        context: Optional[Dict[str, Any]] = None,
        ignore_errors: bool = True
    ):
        """
        Load all discovered plugins
        
        Args:
            context: Optional initialization context for plugins
            ignore_errors: Whether to continue loading if a plugin fails
        """
        # Discover plugins first
        discovered_plugins = self.discover_plugins()
        
        # Load each discovered plugin
        for plugin_class in discovered_plugins:
            try:
                self.load_plugin(plugin_class, context)
            except Exception as e:
                if not ignore_errors:
                    raise
                logger.warning(f"Could not load plugin {plugin_class.__name__}: {e}")

# Global plugin manager instance
plugin_manager = PluginManager()

# Expose key functions and types
__all__ = [
    'PluginManager', 
    'PluginBase', 
    'plugin_manager'
]