"""
Advanced Process Monitoring Module for ModHub Central

This module provides enhanced process tracking and management capabilities,
including resource usage tracking, process lifecycle monitoring, and
intelligent filtering.
"""

import psutil
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import time
import re

logger = logging.getLogger(__name__)

@dataclass
class ProcessInfo:
    """Comprehensive process information tracking"""
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
    cmdline: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_monitored: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

class AdvancedProcessMonitor:
    """
    Enhanced process monitoring with advanced tracking and management capabilities
    """
    def __init__(
        self, 
        scan_interval: int = 5, 
        max_tracked_processes: int = 500,
        resource_threshold_cpu: float = 70.0,
        resource_threshold_memory: float = 80.0
    ):
        self._tracked_processes: Dict[int, ProcessInfo] = {}
        self._monitored_callbacks: Dict[str, Callable] = {}
        self._scan_interval = scan_interval
        self._max_tracked_processes = max_tracked_processes
        self._resource_thresholds = {
            'cpu': resource_threshold_cpu,
            'memory': resource_threshold_memory
        }
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Process categorization rules
        self._categorization_rules = [
            # Gaming applications
            {'pattern': r'steam\.exe|origin\.exe|epicgames\.exe', 'tag': 'gaming'},
            # Media applications
            {'pattern': r'vlc\.exe|spotify\.exe|netflix\.exe', 'tag': 'media'},
            # Development tools
            {'pattern': r'code\.exe|idea64\.exe|pycharm64\.exe', 'tag': 'development'}
        ]

    def start_monitoring(self):
        """Start continuous process monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.warning("Process monitoring already running")
            return

        self._stop_event.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            daemon=True
        )
        self._monitoring_thread.start()
        logger.info("Advanced process monitoring started")

    def stop_monitoring(self):
        """Stop process monitoring"""
        if self._monitoring_thread:
            self._stop_event.set()
            self._monitoring_thread.join(timeout=5)
            logger.info("Process monitoring stopped")

    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while not self._stop_event.is_set():
            try:
                self._scan_processes()
                self._check_resource_thresholds()
                time.sleep(self._scan_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self._scan_interval)

    def _scan_processes(self):
        """Scan and update current system processes"""
        current_processes = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'status', 'cmdline']):
            try:
                pid = proc.info['pid']
                
                # Apply categorization rules
                tags = self._categorize_process(proc.info['name'])
                
                # Create or update process info
                process_info = ProcessInfo(
                    pid=pid,
                    name=proc.info['name'],
                    exe_path=proc.info.get('exe'),
                    status=proc.info.get('status', 'unknown'),
                    cmdline=proc.info.get('cmdline', []),
                    tags=tags
                )
                
                # Update dynamic metrics
                try:
                    with proc.oneshot():
                        process_info.cpu_usage = proc.cpu_percent()
                        process_info.memory_usage = proc.memory_percent()
                        process_info.threads_count = proc.num_threads()
                        
                        # I/O counters if available
                        try:
                            io_counters = proc.io_counters()
                            process_info.io_read_bytes = io_counters.read_bytes
                            process_info.io_write_bytes = io_counters.write_bytes
                        except Exception:
                            pass
                        
                        # Parent process tracking
                        try:
                            parent = proc.parent()
                            process_info.parent_pid = parent.pid if parent else None
                        except Exception:
                            pass
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                
                current_processes[pid] = process_info
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Update tracked processes
        self._tracked_processes = current_processes

    def _categorize_process(self, process_name: str) -> List[str]:
        """Categorize processes based on predefined rules"""
        tags = []
        for rule in self._categorization_rules:
            if re.search(rule['pattern'], process_name, re.IGNORECASE):
                tags.append(rule['tag'])
        return tags

    def _check_resource_thresholds(self):
        """Check processes exceeding resource thresholds"""
        high_resource_processes = [
            process for process in self._tracked_processes.values()
            if (process.cpu_usage > self._resource_thresholds['cpu'] or
                process.memory_usage > self._resource_thresholds['memory'])
        ]
        
        if high_resource_processes:
            self._trigger_high_resource_event(high_resource_processes)

    def _trigger_high_resource_event(self, processes: List[ProcessInfo]):
        """Trigger events or callbacks for high-resource processes"""
        for process in processes:
            logger.warning(
                f"High resource usage detected: {process.name} "
                f"(PID: {process.pid}, CPU: {process.cpu_usage}%, "
                f"Memory: {process.memory_usage}%)"
            )
            # TODO: Implement more sophisticated handling

    def get_processes_by_tag(self, tag: str) -> List[ProcessInfo]:
        """Retrieve processes with a specific tag"""
        return [
            process for process in self._tracked_processes.values() 
            if tag in process.tags
        ]

    def register_process_callback(
        self, 
        callback: Callable, 
        process_name_pattern: Optional[str] = None,
        tag: Optional[str] = None
    ):
        """
        Register a callback for specific process events
        
        Args:
            callback: Function to call on process event
            process_name_pattern: Regex pattern to match process names
            tag: Process tag to match
        """
        key = f"{process_name_pattern or ''}:{tag or ''}"
        self._monitored_callbacks[key] = callback