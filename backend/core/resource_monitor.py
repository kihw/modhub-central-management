# backend/core/resource_monitor.py
import psutil
import logging
from typing import Dict, List, Optional, Callable, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Queue
import threading
import time
import os
import re
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class ResourceUsage:
    """Class to store system resource usage metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    total_memory: int = 0
    available_memory: int = 0
    total_disk: int = 0
    available_disk: int = 0
    processes_count: int = 0
    temperature: List[Dict[str, Any]] = field(default_factory=list)
    gpu_usage: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource usage to a dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "total_memory": self.total_memory,
            "available_memory": self.available_memory,
            "total_disk": self.total_disk,
            "available_disk": self.available_disk,
            "processes_count": self.processes_count,
            "temperature": self.temperature,
            "gpu_usage": self.gpu_usage
        }

class SystemResourceMonitor:
    """Monitor system resource usage over time"""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self, 
        interval: float = 5.0, 
        history_length: int = 100,
        thresholds: Optional[Dict[str, float]] = None
    ):
        # Avoid re-initialization (singleton pattern)
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._interval = max(1.0, interval)
        self._history_length = max(10, min(10000, history_length))
        self._resource_history = deque(maxlen=self._history_length)
        self._critical_events = deque(maxlen=1000)
        self._peak_metrics = {
            'cpu_peak': 0.0,
            'memory_peak': 0.0,
            'disk_peak': 0.0,
            'gpu_peak': 0.0
        }
        self._thresholds = thresholds or {
            'cpu': 80.0,
            'memory': 80.0,
            'disk': 90.0,
            'temperature': 80.0
        }
        self._monitoring_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._initialized = True
        
        logger.info("SystemResourceMonitor initialized")

    def _collect_system_metrics(self) -> ResourceUsage:
        """Collect current system resource metrics with improved error handling"""
        try:
            # Get CPU usage
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
            except Exception as e:
                logger.warning(f"Error getting CPU percent: {e}")
                cpu_percent = 0.0

            # Get memory usage
            try:
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                total_memory = memory.total
                available_memory = memory.available
            except Exception as e:
                logger.warning(f"Error getting memory info: {e}")
                memory_percent = 0.0
                total_memory = 0
                available_memory = 0

            # Get disk usage (root or home directory)
            try:
                disk_path = os.path.expanduser('~')
                disk = psutil.disk_usage(disk_path)
                disk_percent = disk.percent
                total_disk = disk.total
                available_disk = disk.free
            except Exception as e:
                logger.warning(f"Error getting disk usage for home directory: {e}")
                # Fallback to root directory
                try:
                    disk = psutil.disk_usage('/')
                    disk_percent = disk.percent
                    total_disk = disk.total
                    available_disk = disk.free
                except Exception as e2:
                    logger.warning(f"Error getting disk usage for root directory: {e2}")
                    disk_percent = 0.0
                    total_disk = 0
                    available_disk = 0

            # Get process count
            try:
                processes = list(psutil.process_iter())
                processes_count = len(processes)
            except Exception as e:
                logger.warning(f"Error getting process count: {e}")
                processes_count = 0

            # Get temperature information
            try:
                temperatures = self._collect_temperatures()
            except Exception as e:
                logger.warning(f"Error collecting temperature data: {e}")
                temperatures = []

            # Get GPU usage information
            try:
                gpu_usage = self._collect_gpu_metrics()
            except Exception as e:
                logger.warning(f"Error collecting GPU metrics: {e}")
                gpu_usage = []

            # Create ResourceUsage object
            resource_usage = ResourceUsage(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_usage=memory_percent,
                disk_usage=disk_percent,
                total_memory=total_memory,
                available_memory=available_memory,
                total_disk=total_disk,
                available_disk=available_disk,
                processes_count=processes_count,
                temperature=temperatures,
                gpu_usage=gpu_usage
            )

            # Update peak metrics
            self._update_peak_metrics(resource_usage)

            # Check for critical resource usage
            self._check_critical_thresholds(resource_usage)

            return resource_usage

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}", exc_info=True)
            # Retourner un objet ResourceUsage avec des valeurs par défaut
            return ResourceUsage(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                total_memory=0,
                available_memory=0,
                total_disk=0,
                available_disk=0,
                processes_count=0,
                temperature=[],
                gpu_usage=[]
            )

    def _collect_gpu_metrics(self) -> List[Dict[str, Any]]:
        """Collect GPU metrics with improved error handling"""
        gpu_metrics = []

        # Try importing and using GPUtil for NVIDIA GPUs
        try:
            import GPUtil
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    try:
                        gpu_metrics.append({
                            "id": i,
                            "name": gpu.name,
                            "load": gpu.load * 100 if gpu.load is not None else 0.0,  # Convert to percentage
                            "memory_usage": gpu.memoryUtil * 100 if gpu.memoryUtil is not None else 0.0,  # Convert to percentage
                            "temperature": gpu.temperature if gpu.temperature is not None else 0.0,
                            "memory_total": gpu.memoryTotal if gpu.memoryTotal is not None else 0,
                            "memory_used": gpu.memoryUsed if gpu.memoryUsed is not None else 0
                        })
                    except Exception as e:
                        logger.warning(f"Error processing GPU {i}: {e}")
            except Exception as e:
                logger.warning(f"Error getting GPUs with GPUtil: {e}")
        except ImportError:
            # GPUtil not available, try other approaches
            try:
                # Tentative avec nvidia-smi via subprocess (Windows/Linux)
                import subprocess
                import json

                try:
                    result = subprocess.run(
                        ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu', '--format=csv,noheader'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )

                    if result.returncode == 0:
                        for i, line in enumerate(result.stdout.strip().split('\n')):
                            parts = line.split(', ')
                            if len(parts) >= 6:
                                try:
                                    utilization = float(parts[2].replace(' %', ''))
                                    mem_used = float(parts[3].replace(' MiB', ''))
                                    mem_total = float(parts[4].replace(' MiB', ''))
                                    temp = float(parts[5])

                                    gpu_metrics.append({
                                        "id": i,
                                        "name": parts[1],
                                        "load": utilization,
                                        "memory_usage": (mem_used / mem_total * 100) if mem_total > 0 else 0.0,
                                        "temperature": temp,
                                        "memory_total": mem_total,
                                        "memory_used": mem_used
                                    })
                                except (ValueError, IndexError) as e:
                                    logger.warning(f"Error parsing nvidia-smi output for GPU {i}: {e}")
                except (subprocess.SubprocessError, FileNotFoundError) as e:
                    logger.debug(f"nvidia-smi command failed: {e}")
            except Exception as e:
                logger.debug(f"Error in alternative GPU detection: {e}")

        return gpu_metrics
    # Add this method to the SystemResourceMonitor class in backend/core/resource_monitor.py
    def _collect_temperatures(self) -> List[Dict[str, Any]]:
        """Collect temperature information from system sensors"""
        temperatures = []
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if hasattr(entry, "current") and entry.current is not None:
                                temperatures.append({
                                    "sensor": name,
                                    "label": entry.label or "Unknown",
                                    "temperature": entry.current,
                                    "high": entry.high if hasattr(entry, "high") else None,
                                    "critical": entry.critical if hasattr(entry, "critical") else None
                                })
        except Exception as e:
            logger.debug(f"Error collecting temperature data: {e}")

        return temperatures

    def _update_peak_metrics(self, resource_usage: ResourceUsage) -> None:
        """Update peak resource metrics"""
        with self._lock:
            self._peak_metrics['cpu_peak'] = max(self._peak_metrics['cpu_peak'], resource_usage.cpu_percent)
            self._peak_metrics['memory_peak'] = max(self._peak_metrics['memory_peak'], resource_usage.memory_usage)
            self._peak_metrics['disk_peak'] = max(self._peak_metrics['disk_peak'], resource_usage.disk_usage)
            
            # Update GPU peak if available
            if resource_usage.gpu_usage:
                max_gpu_load = max((gpu.get('load', 0) for gpu in resource_usage.gpu_usage), default=0)
                self._peak_metrics['gpu_peak'] = max(self._peak_metrics['gpu_peak'], max_gpu_load)
    
    def _check_critical_thresholds(self, resource_usage: ResourceUsage) -> None:
        """Check if resource usage exceeds critical thresholds"""
        critical_events = []
        
        # Check CPU usage
        if resource_usage.cpu_percent >= self._thresholds.get('cpu', 80.0):
            critical_events.append({
                "type": "cpu",
                "value": resource_usage.cpu_percent,
                "threshold": self._thresholds.get('cpu', 80.0),
                "timestamp": resource_usage.timestamp.isoformat(),
                "message": f"CPU usage ({resource_usage.cpu_percent:.1f}%) exceeded threshold ({self._thresholds.get('cpu', 80.0):.1f}%)"
            })
        
        # Check memory usage
        if resource_usage.memory_usage >= self._thresholds.get('memory', 80.0):
            critical_events.append({
                "type": "memory",
                "value": resource_usage.memory_usage,
                "threshold": self._thresholds.get('memory', 80.0),
                "timestamp": resource_usage.timestamp.isoformat(),
                "message": f"Memory usage ({resource_usage.memory_usage:.1f}%) exceeded threshold ({self._thresholds.get('memory', 80.0):.1f}%)"
            })
        
        # Check disk usage
        if resource_usage.disk_usage >= self._thresholds.get('disk', 90.0):
            critical_events.append({
                "type": "disk",
                "value": resource_usage.disk_usage,
                "threshold": self._thresholds.get('disk', 90.0),
                "timestamp": resource_usage.timestamp.isoformat(),
                "message": f"Disk usage ({resource_usage.disk_usage:.1f}%) exceeded threshold ({self._thresholds.get('disk', 90.0):.1f}%)"
            })
        
        # Check temperature
        for temp in resource_usage.temperature:
            if temp.get('temperature', 0) >= self._thresholds.get('temperature', 80.0):
                critical_events.append({
                    "type": "temperature",
                    "value": temp.get('temperature', 0),
                    "threshold": self._thresholds.get('temperature', 80.0),
                    "sensor": temp.get('sensor', 'Unknown'),
                    "label": temp.get('label', 'Unknown'),
                    "timestamp": resource_usage.timestamp.isoformat(),
                    "message": f"Temperature ({temp.get('temperature', 0):.1f}°C) for {temp.get('label', 'Unknown')} exceeded threshold ({self._thresholds.get('temperature', 80.0):.1f}°C)"
                })
        
        # Add critical events to the queue
        if critical_events:
            with self._lock:
                for event in critical_events:
                    self._critical_events.append(event)
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        logger.info("Resource monitoring loop started")
        
        while not self._stop_event.is_set():
            try:
                # Collect resource metrics
                resource_usage = self._collect_system_metrics()
                
                # Add to history
                with self._lock:
                    self._resource_history.append(resource_usage)
                
                # Wait for next interval
                self._stop_event.wait(self._interval)
                
            except Exception as e:
                logger.error(f"Error in resource monitoring loop: {e}")
                # Shorter wait on error
                self._stop_event.wait(max(1.0, self._interval / 2))
    
    def start_monitoring(self) -> bool:
        """Start the resource monitoring thread"""
        with self._lock:
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                logger.info("Resource monitoring is already running")
                return True
            
            try:
                self._stop_event.clear()
                self._monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    daemon=True,
                    name="ResourceMonitor"
                )
                self._monitoring_thread.start()
                logger.info("Resource monitoring started")
                return True
            except Exception as e:
                logger.error(f"Failed to start resource monitoring: {e}")
                return False
    
    def stop_monitoring(self) -> bool:
        """Stop the resource monitoring thread"""
        with self._lock:
            if not self._monitoring_thread or not self._monitoring_thread.is_alive():
                logger.info("Resource monitoring is not running")
                return True
            
            try:
                self._stop_event.set()
                self._monitoring_thread.join(timeout=5)
                if self._monitoring_thread.is_alive():
                    logger.warning("Resource monitoring thread did not terminate properly")
                logger.info("Resource monitoring stopped")
                return True
            except Exception as e:
                logger.error(f"Error stopping resource monitoring: {e}")
                return False
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self._monitoring_thread is not None and self._monitoring_thread.is_alive()
    
    def get_latest_usage(self) -> Optional[ResourceUsage]:
        """Get the latest resource usage metrics"""
        with self._lock:
            if not self._resource_history:
                return None
            return self._resource_history[-1]
    
    def get_resource_history(
        self, 
        duration: Optional[timedelta] = None,
        limit: Optional[int] = None
    ) -> List[ResourceUsage]:
        """Get resource usage history"""
        with self._lock:
            # Copy the resource history
            history = list(self._resource_history)
            
            # Filter by duration if specified
            if duration:
                cutoff_time = datetime.now() - duration
                history = [usage for usage in history if usage.timestamp >= cutoff_time]
            
            # Apply limit if specified
            if limit and limit > 0:
                history = history[-limit:]
            
            return history
    
    def get_peak_metrics(self) -> Dict[str, float]:
        """Get peak resource metrics"""
        with self._lock:
            return dict(self._peak_metrics)
    
    def reset_peak_metrics(self) -> None:
        """Reset peak resource metrics"""
        with self._lock:
            self._peak_metrics = {
                'cpu_peak': 0.0,
                'memory_peak': 0.0,
                'disk_peak': 0.0,
                'gpu_peak': 0.0
            }
    
    def get_critical_events(
        self, 
        duration: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """Get critical resource events"""
        with self._lock:
            # Copy the critical events
            events = list(self._critical_events)
            
            # Filter by duration if specified
            if duration:
                cutoff_time = datetime.now() - duration
                events = [
                    event for event in events 
                    if datetime.fromisoformat(event['timestamp']) >= cutoff_time
                ]
            
            return events
    
    def set_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Set resource usage thresholds"""
        if not isinstance(thresholds, dict):
            return False
        
        with self._lock:
            for key, value in thresholds.items():
                if key in self._thresholds and isinstance(value, (int, float)):
                    self._thresholds[key] = float(value)
            
            return True

# Create singleton instance
system_resource_monitor = SystemResourceMonitor()

# Try to auto-start monitoring
try:
    system_resource_monitor.start_monitoring()
except Exception as e:
    logger.error(f"Error auto-starting resource monitor: {e}")

# Exports
__all__ = ['ResourceUsage', 'SystemResourceMonitor', 'system_resource_monitor']