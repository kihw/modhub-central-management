import asyncio
import logging
from typing import Dict, Any, Callable, List, Optional, Union
from enum import Enum, auto
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class EventType(Enum):
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

@dataclass(frozen=True)
class SystemEvent:
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: int = field(default=0)

    def __post_init__(self):
        if not isinstance(self.event_type, EventType):
            object.__setattr__(self, 'event_type', EventType[self.event_type])
        if not isinstance(self.details, dict):
            object.__setattr__(self, 'details', dict(self.details))
        object.__setattr__(self, 'severity', min(10, max(0, self.severity)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.event_type.name,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "details": self.details.copy(),
            "severity": self.severity
        }

class EventManager:
    def __init__(self, max_event_history: int = 1000):
        self._event_history: List[SystemEvent] = []
        self._event_handlers: Dict[EventType, List[Callable]] = {}
        self._max_event_history = max(100, min(10000, max_event_history))
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._persistent_handlers: Dict[str, Callable] = {}
        self._running: bool = False
        self._lock = asyncio.Lock()

    async def register_handler(self, event_type: EventType, handler: Callable, persistent_key: Optional[str] = None) -> Callable:
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        async with self._lock:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []

            if persistent_key:
                if persistent_key in self._persistent_handlers:
                    await self.unregister_handler(event_type, persistent_key)
                self._persistent_handlers[persistent_key] = handler
                setattr(handler, '_persistent_key', persistent_key)

            self._event_handlers[event_type].append(handler)
            return handler

    async def unregister_handler(self, event_type: Optional[EventType] = None, persistent_key: Optional[str] = None) -> None:
        async with self._lock:
            if persistent_key:
                self._persistent_handlers.pop(persistent_key, None)
                if event_type and event_type in self._event_handlers:
                    self._event_handlers[event_type] = [h for h in self._event_handlers[event_type]
                                                      if not hasattr(h, '_persistent_key') or h._persistent_key != persistent_key]
            elif event_type:
                self._event_handlers.pop(event_type, None)

    async def emit_event(self, event: Union[SystemEvent, Dict[str, Any]]) -> None:
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

        async with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_event_history:
                self._event_history = self._event_history[-self._max_event_history:]

        await self._event_queue.put(event)

    async def _process_events(self) -> None:
        while self._running:
            try:
                event = await self._event_queue.get()
                handlers = self._event_handlers.get(event.event_type, []).copy()
                
                tasks = [self._execute_handler(handler, event) for handler in handlers]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                self._event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processing error: {str(e)}")

    async def _execute_handler(self, handler: Callable, event: SystemEvent) -> None:
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                await asyncio.get_running_loop().run_in_executor(None, handler, event)
        except Exception as e:
            logger.error(f"Handler error for {event.event_type}: {str(e)}")

    async def start_processing(self) -> None:
        if not self._running:
            self._running = True
            self._processing_task = asyncio.create_task(self._process_events())

    async def stop_processing(self) -> None:
        if self._running:
            self._running = False
            if self._processing_task:
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
                self._processing_task = None
            await self._event_queue.join()

    def get_recent_events(self, event_type: Optional[EventType] = None, 
                         since: Optional[datetime] = None,
                         limit: Optional[int] = None) -> List[SystemEvent]:
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if since:
            events = [e for e in events if e.timestamp >= since]
        if limit:
            events = events[-limit:]
        return events

    def get_event_summary(self, hours: int = 24) -> Dict[EventType, int]:
        cutoff = datetime.now() - timedelta(hours=hours)
        return {event_type: sum(1 for event in self._event_history 
                              if event.event_type == event_type and event.timestamp >= cutoff)
                for event_type in EventType}

    def export_event_log(self, event_type: Optional[EventType] = None,
                        since: Optional[datetime] = None,
                        format: str = 'json') -> Union[List[Dict], str]:
        events = self.get_recent_events(event_type, since)
        
        if format.lower() == 'json':
            return [event.to_dict() for event in events]
        elif format.lower() == 'csv':
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=['type', 'timestamp', 'source', 'severity', 'details'])
            writer.writeheader()
            for event in events:
                event_dict = event.to_dict()
                event_dict['details'] = str(event_dict['details'])
                writer.writerow(event_dict)
            return output.getvalue()
        raise ValueError(f"Unsupported format: {format}")

global_event_manager = EventManager()

async def emit_startup_event(details: Optional[Dict[str, Any]] = None) -> None:
    await global_event_manager.emit_event(SystemEvent(
        event_type=EventType.STARTUP,
        source='system',
        details=details or {},
        severity=5
    ))

async def emit_shutdown_event(details: Optional[Dict[str, Any]] = None) -> None:
    await global_event_manager.emit_event(SystemEvent(
        event_type=EventType.SHUTDOWN,
        source='system',
        details=details or {},
        severity=5
    ))

async def emit_mod_event(event_type: EventType, mod_name: str, details: Optional[Dict[str, Any]] = None) -> None:
    await global_event_manager.emit_event(SystemEvent(
        event_type=event_type,
        source='mod_manager',
        details={'mod_name': mod_name, **(details or {})},
        severity=3
    ))

async def emit_error_event(message: str, details: Optional[Dict[str, Any]] = None, severity: int = 7) -> None:
    await global_event_manager.emit_event(SystemEvent(
        event_type=EventType.CRITICAL_ERROR,
        source='system',
        details={'error_message': message, **(details or {})},
        severity=severity
    ))

__all__ = ['EventType', 'SystemEvent', 'EventManager', 'global_event_manager',
           'emit_startup_event', 'emit_shutdown_event', 'emit_mod_event', 'emit_error_event']