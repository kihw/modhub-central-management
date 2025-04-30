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

async def startup_events():
    """
    Events to run on application startup.
    This function is called by the FastAPI lifespan manager.
    """
    try:
        await emit_startup_event({"source": "application"})
        return True
    except Exception as e:
        await emit_error_event(
            f"Error during startup events: {str(e)}",
            {"error_type": "startup_events"}
        )
        return False

async def shutdown_events():
    """
    Events to run on application shutdown.
    This function is called by the FastAPI lifespan manager.
    """
    try:
        await emit_shutdown_event({"source": "application"})
        return True
    except Exception as e:
        # We can't use emit_error_event here because we might be in the middle of shutdown
        # Just log the error
        import logging
        logging.error(f"Error during shutdown events: {str(e)}")
        return False

__all__ = [
    'EventType',
    'SystemEvent',
    'EventManager',
    'global_event_manager',
    'emit_startup_event',
    'emit_shutdown_event',
    'emit_mod_event',
    'emit_error_event',
    'startup_events',
    'shutdown_events',
]
