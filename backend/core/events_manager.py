"""
Advanced System Event Management Module

Provides a comprehensive event tracking and management system
for ModHub Central, supporting various event types and handlers.
"""

import asyncio
import logging
from typing import Dict, Any, Callable, List, Optional, Union
from enum import Enum, auto
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class EventType(Enum):
    """
    Predefined system event types
    """
    STARTUP = auto()
    SHUTDOWN = auto()
    MOD_ACTIVATED = auto()
    MOD_DEACTIVATED = auto()
    PROCESS_DETECTED = auto()
    RESOURCE_THRESHOLD = auto()
    AUTOMATION_RULE_TRIGGERED = auto()
    CRITICAL_ERROR = auto()
    PERFORMANCE_WARNING = auto()
    SYSTEM_CONFIG_CHANGE = auto()
    PLUGIN_LOADED = auto()
    PLUGIN_UNLOADED = auto()
    DATABASE_MIGRATION = auto()
    SECURITY_EVENT = auto()

@dataclass
class SystemEvent:
    """
    Comprehensive system event representation
    """
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: int = 0  # 0-10 scale, 0 being lowest, 10 being critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation"""
        return {
            "type": self.event_type.name,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "details": self.details,
            "severity": self.severity
        }

class EventManager:
    """
    Advanced event management system with multiple dispatch mechanisms
    """
    
    def __init__(self, max_event_history: int = 1000):
        """
        Initialize event manager
        
        Args:
            max_event_history: Maximum number of events to keep in history
        """
        self._event_history: List[SystemEvent] = []
        self._event_handlers: Dict[EventType, List[Callable]] = {}
        self._max_event_history = max_event_history
        self._event_queue = asyncio.Queue()
        self._processing_task = None
        self._persistent_handlers: Dict[str, Callable] = {}
    
    def register_handler(
        self, 
        event_type: EventType, 
        handler: Callable,
        persistent_key: Optional[str] = None
    ):
        """
        Register an event handler for a specific event type
        
        Args:
            event_type: Type of event to handle
            handler: Async or sync function to process the event
            persistent_key: Optional key to allow overwriting/tracking of handler
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        # Remove existing handler with same persistent key if provided
        if persistent_key:
            self._persistent_handlers[persistent_key] = handler
            # Remove any existing handler with this key
            self._event_handlers[event_type] = [
                h for h in self._event_handlers[event_type] 
                if not (hasattr(h, '_persistent_key') and h._persistent_key == persistent_key)
            ]
            
            # Mark the handler with its persistent key
            handler._persistent_key = persistent_key
        
        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.name}")
        
        return handler
    
    def unregister_handler(
        self, 
        event_type: Optional[EventType] = None, 
        persistent_key: Optional[str] = None
    ):
        """
        Unregister event handlers
        
        Args:
            event_type: Optional specific event type to unregister
            persistent_key: Optional key to remove specific persistent handler
        """
        if persistent_key:
            # Remove from persistent handlers
            if persistent_key in self._persistent_handlers:
                del self._persistent_handlers[persistent_key]
            
            # Remove from event handlers
            if event_type:
                self._event_handlers[event_type] = [
                    h for h in self._event_handlers.get(event_type, [])
                    if not (hasattr(h, '_persistent_key') and h._persistent_key == persistent_key)
                ]
        elif event_type:
            # Clear all handlers for this event type
            if event_type in self._event_handlers:
                del self._event_handlers[event_type]
    
    async def emit_event(self, event: Union[SystemEvent, Dict[str, Any]]):
        """
        Emit a system event
        
        Args:
            event: SystemEvent or dictionary to convert to SystemEvent
        """
        # Convert dictionary to SystemEvent if needed
        if isinstance(event, dict):
            event_type = event.get('event_type')
            if isinstance(event_type, str):
                event_type = EventType[event_type]
            
            event = SystemEvent(
                event_type=event_type,
                source=event.get('source'),
                details=event.get('details', {}),
                severity=event.get('severity', 0)
            )
        
        # Add to event history
        self._event_history.append(event)
        
        # Trim event history if exceeds max
        if len(self._event_history) > self._max_event_history:
            self._event_history = self._event_history[-self._max_event_history:]
        
        # Add to processing queue
        await self._event_queue.put(event)
    
    async def _process_events(self):
        """
        Background task to process events from the queue
        """
        while True:
            try:
                event = await self._event_queue.get()
                
                # Find and execute handlers
                handlers = self._event_handlers.get(event.event_type, [])
                for handler in handlers:
                    try:
                        # Support both async and sync handlers
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event.event_type}: {e}")
                
                self._event_queue.task_done()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in event processing: {e}")
    
    def start_processing(self):
        """
        Start the event processing background task
        """
        if self._processing_task is None or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_events())
            logger.info("Event processing started")
    
    def stop_processing(self):
        """
        Stop the event processing background task
        """
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            logger.info("Event processing stopped")
    
    def get_recent_events(
        self, 
        event_type: Optional[EventType] = None, 
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[SystemEvent]:
        """
        Retrieve recent events with optional filtering
        
        Args:
            event_type: Optional specific event type to filter
            since: Optional time to retrieve events from
            limit: Optional maximum number of events to return
        
        Returns:
            List of filtered events
        """
        events = self._event_history
        
        # Filter by event type
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Filter by time
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # Limit results
        if limit:
            events = events[-limit:]
        
        return events
    
    def get_event_summary(self, hours: int = 24) -> Dict[EventType, int]:
        """
        Get summary of events in the last specified hours
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Dictionary of event type counts
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in self._event_history if e.timestamp >= cutoff]
        
        summary = {}
        for event in recent_events:
            summary[event.event_type] = summary.get(event.event_type, 0) + 1
        
        return summary

    def export_event_log(
        self, 
        event_type: Optional[EventType] = None,
        since: Optional[datetime] = None,
        format: str = 'json'
    ) -> Union[List[Dict], str]:
        """
        Export event logs in various formats
        
        Args:
            event_type: Optional specific event type to filter
            since: Optional time to retrieve events from
            format: Output format (json, csv)
        
        Returns:
            Exported events in specified format
        """
        events = self.get_recent_events(event_type, since)
        
        if format == 'json':
            return [event.to_dict() for event in events]
        
        elif format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            fieldnames = ['type', 'timestamp', 'source', 'severity']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            writer.writeheader()
            for event in events:
                writer.writerow({
                    'type': event.event_type.name,
                    'timestamp': event.timestamp.isoformat(),
                    'source': event.source or '',
                    'severity': event.severity
                })
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Utility functions for easy event emission
async def emit_startup_event(details: Optional[Dict[str, Any]] = None):
    """Emit a startup event"""
    await global_event_manager.emit_event(SystemEvent(
        event_type=EventType.STARTUP,
        source='system',
        details=details or {},
        severity=5
    ))

async def emit_shutdown_event(details: Optional[Dict[str, Any]] = None):
    """Emit a shutdown event"""
    await global_event_manager.emit_event(SystemEvent(
        event_type=EventType.SHUTDOWN,
        source='system',
        details=details or {},
        severity=5
    ))

async def emit_mod_event(
    event_type: EventType, 
    mod_name: str, 
    details: Optional[Dict[str, Any]] = None
):
    """Emit a mod-related event"""
    await global_event_manager.emit_event(SystemEvent(
        event_type=event_type,
        source='mod_manager',
        details={
            'mod_name': mod_name,
            **(details or {})
        },
        severity=3
    ))

async def emit_error_event(
    message: str, 
    details: Optional[Dict[str, Any]] = None, 
    severity: int = 7
):
    """Emit a critical error event"""
    await global_event_manager.emit_event(SystemEvent(
        event_type=EventType.CRITICAL_ERROR,
        source='system',
        details={
            'error_message': message,
            **(details or {})
        },
        severity=severity
    ))

# Global event manager instance
global_event_manager = EventManager()

# Expose key functions and types
__all__ = [
    'EventType', 
    'SystemEvent', 
    'EventManager', 
    'global_event_manager',
    'emit_startup_event',
    'emit_shutdown_event', 
    'emit_mod_event',
    'emit_error_event'
]