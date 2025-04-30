import psutil
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass(frozen=True)
class ProcessInfo:
    process: psutil.Process
    start_time: datetime
    last_seen: datetime = field(default_factory=datetime.now)

class ProcessMonitor:
    def __init__(self):
        self.watched_processes: Dict[str, Callable[[psutil.Process], None]] = {}
        self.current_processes: Dict[str, ProcessInfo] = {}
        self.logger = logging.getLogger(__name__)
        self.is_monitoring: bool = False
        self._scan_interval: float = 1.0
        self._last_scan: datetime = datetime.min

    def add_watch(self, process_name: str, callback: Callable[[psutil.Process], None]) -> bool:
        if not isinstance(process_name, str) or not callable(callback):
            return False
        process_name = process_name.strip().lower()
        if not process_name:
            return False
        self.watched_processes[process_name] = callback
        self.logger.info(f"Added watch for process: {process_name}")
        return True

    def remove_watch(self, process_name: str) -> bool:
        if not isinstance(process_name, str):
            return False
        process_name = process_name.strip().lower()
        if removed := self.watched_processes.pop(process_name, None):
            self.logger.info(f"Removed watch for process: {process_name}")
            return True
        return False

    def scan(self) -> None:
        if not self.is_monitoring:
            return
        current_time = datetime.now()
        if current_time - self._last_scan < timedelta(seconds=self._scan_interval):
            return

        self._last_scan = current_time
        new_processes: Dict[str, ProcessInfo] = {}

        try:
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    proc_name = proc.info['name'].lower()
                    if proc_name in self.watched_processes or proc_name in self.current_processes:
                        if proc_name in self.current_processes:
                            new_processes[proc_name] = ProcessInfo(
                                process=proc,
                                start_time=self.current_processes[proc_name].start_time,
                                last_seen=current_time
                            )
                        else:
                            new_processes[proc_name] = ProcessInfo(
                                process=proc,
                                start_time=datetime.fromtimestamp(proc.info['create_time']),
                                last_seen=current_time
                            )
                            if proc_name in self.watched_processes:
                                self._trigger_callback(proc_name, proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, KeyError):
                    continue
        except Exception as e:
            self.logger.error(f"Error during process scan: {str(e)}")
            return

        self._handle_ended_processes(new_processes)
        self.current_processes = new_processes

    def _trigger_callback(self, proc_name: str, proc: psutil.Process) -> None:
        try:
            if callback := self.watched_processes.get(proc_name):
                callback(proc)
                self.logger.debug(f"Triggered callback for process: {proc_name}")
        except Exception as e:
            self.logger.error(f"Error in process callback for {proc_name}: {str(e)}")

    def _handle_ended_processes(self, new_processes: Dict[str, ProcessInfo]) -> None:
        ended_processes = set(self.current_processes) - set(new_processes)
        for proc_name in ended_processes:
            if proc_name in self.watched_processes:
                self.logger.info(f"Watched process ended: {proc_name}")

    def get_running_processes(self) -> List[str]:
        return sorted(self.current_processes.keys())

    def is_process_running(self, process_name: str) -> bool:
        if not isinstance(process_name, str):
            return False
        return process_name.strip().lower() in self.current_processes

    def start_monitoring(self) -> None:
        if not self.is_monitoring:
            self.is_monitoring = True
            self._last_scan = datetime.min
            self.logger.info("Process monitoring started")

    def stop_monitoring(self) -> None:
        if self.is_monitoring:
            self.is_monitoring = False
            self.current_processes.clear()
            self.logger.info("Process monitoring stopped")

    def get_process_info(self, process_name: str) -> Optional[ProcessInfo]:
        if not isinstance(process_name, str):
            return None
        return self.current_processes.get(process_name.strip().lower())

    def set_scan_interval(self, interval: float) -> None:
        if isinstance(interval, (int, float)) and interval > 0:
            self._scan_interval = float(interval)