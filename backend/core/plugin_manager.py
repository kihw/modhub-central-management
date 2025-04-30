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
    def __init__(self):
        self._metadata: Dict[str, Any] = {
            'id': self.__class__.__name__.lower(),
            'name': self.__class__.__name__,
            'version': '0.1.0',
            'description': self.__class__.__doc__ or 'No description provided',
            'author': 'Unknown',
            'dependencies': [],
            'loaded_at': None,
            'enabled': True,
            'status': 'initialized'
        }
    
    @classmethod
    def get_plugin_metadata(cls) -> Dict[str, Any]:
        return {
            'id': cls.__name__.lower(),
            'name': cls.__name__,
            'module': cls.__module__,
            'description': cls.__doc__ or 'No description provided',
            'version': getattr(cls, '__version__', '0.1.0'),
            'author': getattr(cls, '__author__', 'Unknown')
        }
    
    async def initialize(self, context: Optional[Dict[str, Any]] = None) -> bool:
        try:
            self._metadata['loaded_at'] = datetime.now().isoformat()
            self._metadata['status'] = 'active'
            logger.info(f"Initialized plugin: {self._metadata['name']}")
            return True
        except Exception as e:
            self._metadata['status'] = 'error'
            logger.error(f"Failed to initialize plugin {self._metadata['name']}: {str(e)}")
            capture_exception(e)
            return False
    
    async def shutdown(self) -> bool:
        try:
            self._metadata['status'] = 'shutdown'
            self._metadata['enabled'] = False
            logger.info(f"Shutdown plugin: {self._metadata['name']}")
            return True
        except Exception as e:
            logger.error(f"Error shutting down plugin {self._metadata['name']}: {str(e)}")
            capture_exception(e)
            return False
    
    def enable(self) -> None:
        if not self._metadata['enabled'] and self._metadata['status'] != 'error':
            self._metadata['enabled'] = True
            self._metadata['status'] = 'active'
            
    def disable(self) -> None:
        if self._metadata['enabled']:
            self._metadata['enabled'] = False
            self._metadata['status'] = 'disabled'
    
    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()

class PluginManager:
    def __init__(
        self, 
        plugin_dirs: Optional[List[str]] = None,
        base_plugin_class: Type[PluginBase] = PluginBase
    ):
        self._plugin_dirs = plugin_dirs or [
            str(Path(__file__).parent.parent / "plugins"),
            str(Path.home() / ".modhub" / "plugins")
        ]
        
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._base_plugin_class = base_plugin_class
        self._plugin_dependencies: Dict[str, List[str]] = {}
        self._loading_lock = asyncio.Lock()
        
        for directory in self._plugin_dirs:
            os.makedirs(directory, exist_ok=True)
    
    async def _load_plugin_module(self, module_path: Path) -> Optional[List[Type[PluginBase]]]:
        if not module_path.is_file():
            return None
            
        async with self._loading_lock:
            try:
                module_dir = str(module_path.parent)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)
                    
                module_name = module_path.stem
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    
                module = importlib.import_module(module_name)
                importlib.reload(module)
                
                discovered_plugins = [
                    obj for name, obj in inspect.getmembers(module)
                    if (inspect.isclass(obj) and 
                        issubclass(obj, self._base_plugin_class) and 
                        obj is not self._base_plugin_class)
                ]
                
                return discovered_plugins
                
            except Exception as e:
                logger.error(f"Error loading plugin module {module_path}: {str(e)}")
                capture_exception(e)
                return None
                
            finally:
                if module_dir in sys.path:
                    sys.path.remove(module_dir)
    
    async def discover_plugins(self) -> List[Type[PluginBase]]:
        discovered_plugins = []
        self._plugin_classes.clear()
        
        for directory in self._plugin_dirs:
            plugin_dir = Path(directory)
            
            if not plugin_dir.exists() or not plugin_dir.is_dir():
                continue
                
            for file_path in plugin_dir.glob('*.py'):
                if file_path.stem.startswith('__'):
                    continue
                    
                module_plugins = await self._load_plugin_module(file_path)
                
                if module_plugins:
                    for plugin_class in module_plugins:
                        plugin_id = plugin_class.__name__.lower()
                        if plugin_id not in self._plugin_classes:
                            self._plugin_classes[plugin_id] = plugin_class
                            discovered_plugins.append(plugin_class)
        
        return discovered_plugins
    
    async def load_plugin(
        self, 
        plugin_class: Union[Type[PluginBase], str], 
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[PluginBase]:
        async with self._loading_lock:
            try:
                if isinstance(plugin_class, str):
                    plugin_id = plugin_class.lower()
                    if plugin_id not in self._plugin_classes:
                        raise ValueError(f"Plugin {plugin_class} not found")
                    plugin_class = self._plugin_classes[plugin_id]
                
                plugin_id = plugin_class.__name__.lower()
                
                if plugin_id in self._plugins:
                    existing_plugin = self._plugins[plugin_id]
                    if existing_plugin._metadata['status'] == 'active':
                        return existing_plugin
                    await self.unload_plugin(plugin_id)
                
                plugin_instance = plugin_class()
                if not await plugin_instance.initialize(context):
                    return None
                
                self._plugins[plugin_id] = plugin_instance
                
                await global_event_manager.emit_event(
                    SystemEvent(
                        event_type=EventType.PLUGIN_LOADED,
                        source='plugin_manager',
                        details={
                            'plugin_id': plugin_id,
                            'metadata': plugin_instance.get_metadata()
                        }
                    )
                )
                
                return plugin_instance
                
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_class}: {str(e)}")
                capture_exception(e)
                return None
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        plugin_id = plugin_id.lower()
        if plugin_id not in self._plugins:
            return False
            
        async with self._loading_lock:
            try:
                plugin = self._plugins[plugin_id]
                if await plugin.shutdown():
                    del self._plugins[plugin_id]
                    
                    await global_event_manager.emit_event(
                        SystemEvent(
                            event_type=EventType.PLUGIN_UNLOADED,
                            source='plugin_manager',
                            details={'plugin_id': plugin_id}
                        )
                    )
                    return True
                    
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_id}: {str(e)}")
                capture_exception(e)
                
            return False
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginBase]:
        return self._plugins.get(plugin_id.lower())
    
    def list_available_plugins(self) -> List[Dict[str, Any]]:
        return [
            plugin_class.get_plugin_metadata() 
            for plugin_class in self._plugin_classes.values()
        ]
    
    async def load_all_plugins(
        self, 
        context: Optional[Dict[str, Any]] = None,
        ignore_errors: bool = True
    ) -> Dict[str, bool]:
        results = {}
        discovered_plugins = await self.discover_plugins()
        
        for plugin_class in discovered_plugins:
            plugin_id = plugin_class.__name__.lower()
            try:
                plugin = await self.load_plugin(plugin_class, context)
                results[plugin_id] = bool(plugin)
            except Exception as e:
                results[plugin_id] = False
                if not ignore_errors:
                    raise
                logger.warning(f"Failed to load plugin {plugin_id}: {str(e)}")
                capture_exception(e)
                
        return results

plugin_manager = PluginManager()

__all__ = ['PluginManager', 'PluginBase', 'plugin_manager']