"""
Advanced System Resource Monitoring Module

Provides comprehensive system resource tracking, 
performance metrics, and health monitoring capabilities.
"""

import os
import psutil
import platform
import time
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import shutil

try:
    import GPUtil
    HAS_GPU_UTIL = True
except ImportError:
    HAS_GPU_UTIL = False

logger = logging.getLogger(__name__)

@dataclass
class ResourceUsage:
    """
    Detailed resource usage tracking
    """
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_usage: float = 0.0
    total_memory: int = 0
    available_memory: int = 0
    disk_usage: float = 0.0
    total_disk: int = 0
    available_disk: int = 0
    network_sent: int = 0
    network_received: int = 0
    processes_count: int = 0
    temperature: Optional[List[Dict[str, float]]] = None
    gpu_usage: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert resource usage to dictionary
        
        Returns:
            Dictionary representation of resource usage
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_usage': self.memory_usage,
            'total_memory': self.total_memory,
            'available_memory': self.available_memory,
            'disk_usage': self.disk_usage,
            'total_disk': self.total_disk,
            'available_disk': self.available_disk,
            'network_sent': self.network_sent,
            'network_received': self.network_received,
            'processes_count': self.processes_count,
            'temperature': self.temperature,
            'gpu_usage': self.gpu_usage
        }

class SystemResourceMonitor:
    """
    Comprehensive system resource monitoring with historical tracking
    """
    
    def __init__(
        self, 
        interval: int = 5,  # Seconds between checks
        history_length: int = 288,  # 24 hours at 5-second intervals
        critical_thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize resource monitor
        
        Args:
            interval: Polling interval in seconds
            history_length: Number of historical entries to keep
            critical_thresholds: Resource usage thresholds for alerting
        """
        # Monitoring configuration
        self._interval = interval
        self._history_length = history_length
        
        # Default critical thresholds
        self._thresholds = critical_thresholds or {
            'cpu': 90.0,
            'memory': 90.0,
            'disk': 95.0,
            'gpu': 90.0 if HAS_GPU_UTIL else None,
            'temperature': 85.0  # Celsius
        }
        
        # Resource history
        self._resource_history: List[ResourceUsage] = []
        
        # Threading for background monitoring
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Performance metrics tracking
        self._peak_metrics: Dict[str, float] = {
            'cpu_peak': 0.0,
            'memory_peak': 0.0,
            'disk_peak': 0.0,
            'gpu_peak': 0.0 if HAS_GPU_UTIL else None
        }
        
        # Network usage tracking
        self._last_network_counters = psutil.net_io_counters()
        
        # Event tracking
        self._critical_events: List[Dict[str, Any]] = []
    
    def _collect_system_metrics(self) -> ResourceUsage:
        """
        Collect comprehensive system resource metrics
        
        Returns:
            ResourceUsage instance with current system metrics
        """
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent()
            
            # Memory Usage
            memory = psutil.virtual_memory()
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            
            # Network Usage
            net_counters = psutil.net_io_counters()
            network_sent = net_counters.bytes_sent - self._last_network_counters.bytes_sent
            network_received = net_counters.bytes_recv - self._last_network_counters.bytes_recv
            self._last_network_counters = net_counters
            
            # Process Count
            processes_count = len(psutil.pids())
            
            # GPU Usage (if GPUtil is available)
            gpu_usage = None
            if HAS_GPU_UTIL:
                try:
                    gpus = GPUtil.getGPUs()
                    gpu_usage = [
                        {
                            'gpu_id': gpu.id,
                            'name': gpu.name,
                            'load': gpu.load * 100,
                            'memory_used': gpu.memoryUsed,
                            'memory_total': gpu.memoryTotal,
                            'temperature': gpu.temperature
                        } for gpu in gpus
                    ]
                except Exception as e:
                    logger.warning(f"Error collecting GPU metrics: {e}")
            
            # Temperature collection
            temperatures = self._collect_temperatures()
            
            # Create ResourceUsage instance
            resource_usage = ResourceUsage(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_usage=memory.percent,
                total_memory=memory.total,
                available_memory=memory.available,
                disk_usage=disk.percent,
                total_disk=disk.total,
                available_disk=disk.free,
                network_sent=network_sent,
                network_received=network_received,
                processes_count=processes_count,
                temperature=temperatures,
                gpu_usage=gpu_usage
            )
            
            # Update peak metrics
            self._update_peak_metrics(resource_usage)
            
            return resource_usage
        
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return ResourceUsage()
    
    def _collect_temperatures(self) -> Optional[List[Dict[str, float]]]:
        """
        Collect system temperatures from various sensors
        
        Returns:
            List of temperature readings or None
        """
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            
            return [
                {
                    'sensor': sensor,
                    'current': max(temp.current for temp in temps[sensor]),
                    'high': max(temp.high for temp in temps[sensor] if temp.high is not None),
                    'critical': max(temp.critical for temp in temps[sensor] if temp.critical is not None)
                } for sensor in temps
            ]
        except Exception as e:
            logger.warning(f"Error collecting temperatures: {e}")
            return None
    
    def _update_peak_metrics(self, resource_usage: ResourceUsage):
        """
        Update peak resource usage metrics
        
        Args:
            resource_usage: Current resource usage
        """
        # Update peak CPU usage
        self._peak_metrics['cpu_peak'] = max(
            self._peak_metrics['cpu_peak'], 
            resource_usage.cpu_percent
        )
        
        # Update peak memory usage
        self._peak_metrics['memory_peak'] = max(
            self._peak_metrics['memory_peak'], 
            resource_usage.memory_usage
        )
        
        # Update peak disk usage
        self._peak_metrics['disk_peak'] = max(
            self._peak_metrics['disk_peak'], 
            resource_usage.disk_usage
        )
        
        # Update peak GPU usage if available
        if HAS_GPU_UTIL and resource_usage.gpu_usage:
            peak_gpu_usage = max(
                gpu['load'] for gpu in resource_usage.gpu_usage
            )
            self._peak_metrics['gpu_peak'] = max(
                self._peak_metrics.get('gpu_peak', 0), 
                peak_gpu_usage
            )
    
    def _check_critical_thresholds(self, resource_usage: ResourceUsage):
        """
        Check resource usage against critical thresholds
        
        Args:
            resource_usage: Current resource usage
        """
        current_time = datetime.now()
        
        # Check CPU threshold
        if (resource_usage.cpu_percent >= self._thresholds.get('cpu', float('inf'))):
            self._critical_events.append({
                'type': 'cpu_high',
                'timestamp': current_time,
                'value': resource_usage.cpu_percent,
                'threshold': self._thresholds['cpu']
            })
        
        # Check memory threshold
        if (resource_usage.memory_usage >= self._thresholds.get('memory', float('inf'))):
            self._critical_events.append({
                'type': 'memory_high',
                'timestamp': current_time,
                'value': resource_usage.memory_usage,
                'threshold': self._thresholds['memory']
            })
        
        # Check disk threshold
        if (resource_usage.disk_usage >= self._thresholds.get('disk', float('inf'))):
            self._critical_events.append({
                'type': 'disk_full',
                'timestamp': current_time,
                'value': resource_usage.disk_usage,
                'threshold': self._thresholds['disk']
            })
        
        # Check GPU threshold
        if (HAS_GPU_UTIL and resource_usage.gpu_usage and 
            any(gpu['load'] >= self._thresholds.get('gpu', float('inf')) for gpu in resource_usage.gpu_usage)):
            self._critical_events.append({
                'type': 'gpu_high',
                'timestamp': current_time,
                'value': max(gpu['load'] for gpu in resource_usage.gpu_usage),
                'threshold': self._thresholds['gpu']
            })
        
        # Limit critical events
        if len(self._critical_events) > 100:
            self._critical_events = self._critical_events[-100:]
    
    def _monitoring_loop(self):
        """
        Background monitoring loop
        """
        while not self._stop_event.is_set():
            try:
                # Collect system metrics
                resource_usage = self._collect_system_metrics()
                
                # Add to resource history
                self._resource_history.append(resource_usage)
                
                # Trim history if exceeds length
                if len(self._resource_history) > self._history_length:
                    self._resource_history = self._resource_history[-self._history_length:]
                
                # Check critical thresholds
                self._check_critical_thresholds(resource_usage)
                
                # Wait for next interval
                time.sleep(self._interval)
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                
                # Wait before retrying
                time.sleep(self._interval)
    
    def start_monitoring(self):
        """
        Start background resource monitoring
        """
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.warning("Monitoring already running")
            return
        
        # Reset state
        self._stop_event.clear()
        self._resource_history.clear()
        self._critical_events.clear()
        
        # Start monitoring thread
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, 
            daemon=True
        )
        self._monitoring_thread.start()
        
        logger.info("System resource monitoring started")
    
    def stop_monitoring(self):
        """
        Stop background resource monitoring
        """
        if self._monitoring_thread:
            self._stop_event.set()
            self._monitoring_thread.join(timeout=5)
            logger.info("System resource monitoring stopped")
    
    def get_resource_history(
        self, 
        duration: Optional[timedelta] = None
    ) -> List[ResourceUsage]:
        """
        Retrieve resource usage history
        
        Args:
            duration: Optional time duration to retrieve history for
        
        Returns:
            List of ResourceUsage instances
        """
        if not duration:
            return self._resource_history
        
        cutoff_time = datetime.now() - duration
        return [
            usage for usage in self._resource_history 
            if usage.timestamp >= cutoff_time
        ]
    
    def get_peak_metrics(self) -> Dict[str, float]:
        """
        Get peak resource usage metrics
        
        Returns:
            Dictionary of peak metrics
        """
        return self._peak_metrics
    
    def get_critical_events(
        self, 
        duration: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve critical resource events
        
        Args:
            duration: Optional time duration to retrieve events for
        
        Returns:
            List of critical events
        """
        if not duration:
            return self._critical_events
        
        cutoff_time = datetime.now() - duration
        return [
            event for event in self._critical_events 
            if event['timestamp'] >= cutoff_time
        ]

# Global system resource monitor instance
system_resource_monitor = SystemResourceMonitor()

# Expose key functions and types
__all__ = [
    'SystemResourceMonitor', 
    'ResourceUsage', 
    'system_resource_monitor'
]