"""
Events system for ModHub Central.
This module exports components from events_manager.py for backward compatibility.
"""

from .events_manager import (
    EventType, 
    SystemEvent, 
    EventManager, 
    global_event_manager,
    emit_startup_event,
    emit_shutdown_event,
    emit_mod_event,
    emit_error_event,
)

__all__ = [
    'EventType',
    'SystemEvent',
    'EventManager',
    'global_event_manager',
    'emit_startup_event',
    'emit_shutdown_event',
    'emit_mod_event',
    'emit_error_event',
]
