# Create a new file: backend/core/api_utils.py

import logging
from typing import Dict, Any, Optional, List, Union, Tuple, Type
from fastapi import HTTPException, status

from .mods.mod_manager import ModManager 
from .process_monitor import ProcessMonitor
from .events_manager import global_event_manager, EventType, SystemEvent
from .resource_monitor import system_resource_monitor
from db.models import Mod as DbMod
from db.schemas import ModCreate, ModUpdate

logger = logging.getLogger(__name__)

# Get singleton instances
mod_manager = ModManager()
process_monitor = ProcessMonitor()

def sync_mods_from_db(mods: List[DbMod]) -> Tuple[int, int]:
    """
    Sync database mods with mod manager
    Returns (success_count, error_count)
    """
    success = 0
    errors = 0
    
    for db_mod in mods:
        # Check if mod should be active
        if db_mod.is_active:
            try:
                if mod_manager.activate_mod(db_mod.type, db_mod.config):
                    success += 1
                else:
                    errors += 1
                    logger.error(f"Failed to activate mod: {db_mod.name} (type: {db_mod.type})")
            except Exception as e:
                errors += 1
                logger.error(f"Error activating mod {db_mod.name}: {e}")
    
    return success, errors

def db_mod_to_manager(db_mod: DbMod) -> bool:
    """
    Convert a database mod to mod manager format and register/update it
    """
    try:
        # Check if mod exists first
        if db_mod.type in mod_manager.get_all_mods():
            # Update existing mod
            mod_instance = mod_manager.get_mod(db_mod.type)
            if mod_instance and hasattr(mod_instance, 'instance'):
                mod_instance.instance.update_config(db_mod.config)
                return True
                
        # Determine mod class based on type
        mod_type = db_mod.type.lower()
        if mod_type == "gaming":
            from .mods.gaming_mod import GamingMod
            mod_instance = GamingMod()
        elif mod_type == "night":
            from .mods.night_mod import NightMod
            mod_instance = NightMod()
        elif mod_type == "media":
            from .mods.media_mod import MediaMod
            mod_instance = MediaMod()
        else:
            logger.error(f"Unknown mod type: {mod_type}")
            return False
            
        # Update mod config
        mod_instance.update_config(db_mod.config)
        
        # Register with mod manager
        return mod_manager.register_mod(db_mod.type, mod_instance)
    except Exception as e:
        logger.error(f"Error converting DB mod to manager: {e}")
        return False

def get_detailed_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information
    """
    try:
        # Get basic system info
        from .system_info import get_system_info
        system_info = get_system_info()
        
        # Add resource usage
        resources = system_resource_monitor.get_resource_history(limit=1)
        if resources:
            resource_usage = resources[0].to_dict()
        else:
            from .system_info import get_resource_usage
            resource_usage = get_resource_usage()
            
        # Add active mods
        active_mods = mod_manager.get_active_mods()
        
        # Add recent events
        recent_events = global_event_manager.get_recent_events(limit=10)
        events_data = [event.to_dict() for event in recent_events]
        
        return {
            "system": system_info,
            "resources": resource_usage,
            "active_mods": [mod.metadata.name for mod in active_mods.values()],
            "active_mods_count": len(active_mods),
            "recent_events": events_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting detailed system info: {e}")
        return {"error": str(e)}