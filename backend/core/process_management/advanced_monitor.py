import psutil
import logging
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Queue
import threading
import time
import re
from weakref import WeakValueDictionary

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    name: str
    exe_path: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    threads_count: int = 0
    status: str = 'running'
    parent_pid: Optional[int] = None
    cmdline: tuple[str, ...] = field(default_factory=tuple)
    tags: frozenset[str] = field(default_factory=frozenset)
    is_monitored: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

class AdvancedProcessMonitor:
    PROCESS_CATEGORIES = (
        {'pattern': r'steam\.exe|origin\.exe|epicgames\.exe|game|unity\.exe', 'tag': 'gaming'},
        {'pattern': r'vlc\.exe|spotify\.exe|netflix\.exe|media|player|audio', 'tag': 'media'},
        {'pattern': r'code\.exe|idea64\.exe|pycharm64\.exe|dev|studio|compiler', 'tag': 'development'}
    )

    def __init__(
        self, 
        scan_interval: float = 5.0, 
        max_tracked_processes: int = 500,
        resource_threshold_cpu: float = 70.0,
        resource_threshold_memory: float = 80.0
    ):
        self._tracked_processes = WeakValueDictionary()
        self._monitored_callbacks: Dict[str, Set[Callable]] = {}
        self._scan_interval = max(0.1, min(scan_interval, 60.0))
        self._max_tracked_processes = max(10, min(max_tracked_processes, 1000))
        self._resource_thresholds = {
            'cpu': min(100.0, max(0.0, resource_threshold_cpu)),
            'memory': min(100.0, max(0.0, resource_threshold_memory))
        }
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._event_queue: Queue = Queue(maxsize=1000)
        self._process_patterns = {cat['tag']: re.compile(cat['pattern'], re.IGNORECASE) for cat in self.PROCESS_CATEGORIES}

    def start_monitoring(self) -> bool:
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return False
        
        self._stop_event.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ProcessMonitor"
        )
        self._monitoring_thread.start()
        return True
    
    def is_monitoring(self) -> bool:
        return self._monitoring_thread is not None and self._monitoring_thread.is_alive()

    def stop_monitoring(self) -> bool:
        if not self._monitoring_thread:
            return False
            
        self._stop_event.set()
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        self._tracked_processes.clear()
        return True

    def _monitoring_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._scan_processes()
                self._process_events()
                self._check_resource_thresholds()
                time.sleep(self._scan_interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}", exc_info=True)
                time.sleep(max(1.0, self._scan_interval / 2))

    def _scan_processes(self) -> None:
        if not self.is_monitoring:
            return

        current_time = datetime.now()
        if current_time - self._last_scan < timedelta(seconds=self._scan_interval):
            return

        self._last_scan = current_time
        new_processes: Dict[str, ProcessInfo] = {}

        try:
            process_list = list(psutil.process_iter(['pid', 'name', 'create_time']))

            # First, build a map of all current processes for efficient lookup
            current_proc_map = {}
            for proc in process_list:
                try:
                    proc_name = proc.info['name'].lower()
                    current_proc_map[proc_name] = proc
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, KeyError):
                    continue

            # Now check watched and previously seen processes
            for proc_name in set(list(self.watched_processes.keys()) + list(self.current_processes.keys())):
                proc = current_proc_map.get(proc_name)

                if proc:
                    # Process still exists
                    if proc_name in self.current_processes:
                        # Update existing process info
                        new_processes[proc_name] = ProcessInfo(
                            process=proc,
                            start_time=self.current_processes[proc_name].start_time,
                            last_seen=current_time
                        )
                    else:
                        # New process - trigger callback if watched
                        try:
                            create_time = datetime.fromtimestamp(proc.info['create_time'])
                        except (KeyError, TypeError, ValueError, OSError):
                            create_time = current_time

                        new_processes[proc_name] = ProcessInfo(
                            process=proc,
                            start_time=create_time,
                            last_seen=current_time
                        )

                        if proc_name in self.watched_processes:
                            self._trigger_callback(proc_name, proc)

            # Update the process list with new info
            self.current_processes = new_processes

        except Exception as e:
            self.logger.error(f"Error during process scan: {str(e)}")

    def _create_process_info(self, proc: psutil.Process) -> Optional[ProcessInfo]:
        try:
            proc_info = proc.info
            process_info = ProcessInfo(
                pid=proc_info['pid'],
                name=proc_info['name'],
                exe_path=proc_info.get('exe'),
                status=proc_info.get('status', 'unknown'),
                cmdline=tuple(proc_info.get('cmdline', ())),
                tags=frozenset(self._categorize_process(proc_info['name'])),
                last_updated=datetime.now()
            )

            with proc.oneshot():
                process_info = ProcessInfo(
                    **{**process_info.__dict__,
                    'cpu_usage': proc.cpu_percent(),
                    'memory_usage': proc.memory_percent(),
                    'threads_count': proc.num_threads(),
                    'io_read_bytes': proc.io_counters().read_bytes,
                    'io_write_bytes': proc.io_counters().write_bytes,
                    'parent_pid': proc.parent().pid if proc.parent() else None}
                )

            return process_info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def _categorize_process(self, process_name: str) -> Set[str]:
        return {tag for tag, pattern in self._process_patterns.items() if pattern.search(process_name)}

    def _check_resource_thresholds(self) -> None:
        high_resource_processes = [
            process for process in self._tracked_processes.values()
            if (process.cpu_usage > self._resource_thresholds['cpu'] or
                process.memory_usage > self._resource_thresholds['memory'])
        ]
        
        if high_resource_processes and not self._event_queue.full():
            self._event_queue.put(('high_resource', tuple(high_resource_processes)))

    def _process_events(self) -> None:
        while not self._event_queue.empty():
            event_type, data = self._event_queue.get_nowait()
            if event_type == 'high_resource':
                self._handle_high_resource_processes(data)
            self._event_queue.task_done()

    def _handle_high_resource_processes(self, processes: tuple[ProcessInfo, ...]) -> None:
        for process in processes:
            for callback_key, callbacks in self._monitored_callbacks.items():
                pattern, tag = callback_key.split(':')
                if (not pattern or re.search(pattern, process.name, re.IGNORECASE)) and \
                   (not tag or tag in process.tags):
                    for callback in callbacks:
                        try:
                            callback(process)
                        except Exception as e:
                            logger.error(f"Callback error for {process.name}: {e}", exc_info=True)

    def get_processes_by_tag(self, tag: str) -> tuple[ProcessInfo, ...]:
        return tuple(proc for proc in self._tracked_processes.values() if tag in proc.tags)

    def register_process_callback(
        self, 
        callback: Callable[[ProcessInfo], None],
        process_name_pattern: str = '',
        tag: str = ''
    ) -> bool:
        if not callable(callback):
            return False
        key = f"{process_name_pattern}:{tag}"
        if key not in self._monitored_callbacks:
            self._monitored_callbacks[key] = set()
        self._monitored_callbacks[key].add(callback)
        return True