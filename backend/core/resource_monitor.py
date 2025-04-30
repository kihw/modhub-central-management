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
from concurrent.futures import ThreadPoolExecutor

try:
    import GPUtil
    HAS_GPU_UTIL = True
except ImportError:
    HAS_GPU_UTIL = False

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ResourceUsage:
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
    temperature: Optional[List[Dict[str, float]]] = field(default_factory=list)
    gpu_usage: Optional[List[Dict[str, Any]]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {k: round(v, 2) if isinstance(v, float) else v for k, v in self.__dict__.items()}

class SystemResourceMonitor:
    def __init__(
        self,
        interval: int = 5,
        history_length: int = 288,
        critical_thresholds: Optional[Dict[str, float]] = None,
        max_workers: int = 4
    ):
        self._interval = max(1, interval)
        self._history_length = max(1, history_length)
        self._thresholds = {
            'cpu': 90.0,
            'memory': 90.0,
            'disk': 95.0,
            'gpu': 90.0 if HAS_GPU_UTIL else None,
            'temperature': 85.0,
            **(critical_thresholds or {})
        }
        self._resource_history: List[ResourceUsage] = []
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._peak_metrics = {metric: 0.0 for metric in ['cpu_peak', 'memory_peak', 'disk_peak', 'gpu_peak']}
        self._last_network_counters = psutil.net_io_counters()
        self._critical_events: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def _collect_system_metrics(self) -> ResourceUsage:
        try:
            with self._lock:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                net_counters = psutil.net_io_counters()
                network_sent = max(0, net_counters.bytes_sent - self._last_network_counters.bytes_sent)
                network_received = max(0, net_counters.bytes_recv - self._last_network_counters.bytes_recv)
                self._last_network_counters = net_counters

            gpu_future = self._executor.submit(self._collect_gpu_metrics) if HAS_GPU_UTIL else None
            temp_future = self._executor.submit(self._collect_temperatures)

            gpu_usage = gpu_future.result() if gpu_future else []
            temperatures = temp_future.result()

            return ResourceUsage(
                cpu_percent=cpu_percent,
                memory_usage=memory.percent,
                total_memory=memory.total,
                available_memory=memory.available,
                disk_usage=disk.percent,
                total_disk=disk.total,
                available_disk=disk.free,
                network_sent=network_sent,
                network_received=network_received,
                processes_count=len(psutil.pids()),
                temperature=temperatures,
                gpu_usage=gpu_usage
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return ResourceUsage()

    def _collect_gpu_metrics(self) -> List[Dict[str, Any]]:
        try:
            if not HAS_GPU_UTIL:
                return []
            gpus = GPUtil.getGPUs()
            return [{
                'gpu_id': gpu.id,
                'name': gpu.name,
                'load': gpu.load * 100,
                'memory_used': gpu.memoryUsed,
                'memory_total': gpu.memoryTotal,
                'temperature': gpu.temperature
            } for gpu in gpus]
        except Exception as e:
            logger.warning(f"Failed to collect GPU metrics: {e}")
            return []

    def _collect_temperatures(self) -> List[Dict[str, float]]:
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return []
            return [{
                'sensor': sensor,
                'current': max(temp.current for temp in sensor_temps),
                'high': max((temp.high or 0) for temp in sensor_temps),
                'critical': max((temp.critical or 0) for temp in sensor_temps)
            } for sensor, sensor_temps in temps.items()]
        except Exception as e:
            logger.warning(f"Failed to collect temperature metrics: {e}")
            return []

    def _update_peak_metrics(self, resource_usage: ResourceUsage) -> None:
        with self._lock:
            self._peak_metrics.update({
                'cpu_peak': max(self._peak_metrics['cpu_peak'], resource_usage.cpu_percent),
                'memory_peak': max(self._peak_metrics['memory_peak'], resource_usage.memory_usage),
                'disk_peak': max(self._peak_metrics['disk_peak'], resource_usage.disk_usage),
                'gpu_peak': max(self._peak_metrics['gpu_peak'], 
                              max((gpu['load'] for gpu in resource_usage.gpu_usage), default=0.0))
            })

    def _check_critical_thresholds(self, resource_usage: ResourceUsage) -> None:
        current_time = datetime.now()
        thresholds_map = {
            ('cpu_high', 'cpu_percent', 'cpu'),
            ('memory_high', 'memory_usage', 'memory'),
            ('disk_full', 'disk_usage', 'disk')
        }

        new_events = []
        for event_type, metric_name, threshold_key in thresholds_map:
            value = getattr(resource_usage, metric_name)
            if value >= self._thresholds[threshold_key]:
                new_events.append({
                    'type': event_type,
                    'timestamp': current_time,
                    'value': value,
                    'threshold': self._thresholds[threshold_key]
                })

        if HAS_GPU_UTIL and resource_usage.gpu_usage:
            max_gpu_load = max(gpu['load'] for gpu in resource_usage.gpu_usage)
            if max_gpu_load >= self._thresholds['gpu']:
                new_events.append({
                    'type': 'gpu_high',
                    'timestamp': current_time,
                    'value': max_gpu_load,
                    'threshold': self._thresholds['gpu']
                })

        with self._lock:
            self._critical_events.extend(new_events)
            self._critical_events = self._critical_events[-100:]

    def _monitoring_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                resource_usage = self._collect_system_metrics()
                with self._lock:
                    self._resource_history.append(resource_usage)
                    self._resource_history = self._resource_history[-self._history_length:]
                self._update_peak_metrics(resource_usage)
                self._check_critical_thresholds(resource_usage)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
            finally:
                time.sleep(self._interval)

    def start_monitoring(self) -> None:
        with self._lock:
            if not self._monitoring_thread or not self._monitoring_thread.is_alive():
                self._stop_event.clear()
                self._resource_history.clear()
                self._critical_events.clear()
                self._monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    daemon=True
                )
                self._monitoring_thread.start()

    def stop_monitoring(self) -> None:
        self._stop_event.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        self._executor.shutdown(wait=True)

    def get_resource_history(self, duration: Optional[timedelta] = None) -> List[ResourceUsage]:
        with self._lock:
            if not duration:
                return self._resource_history.copy()
            cutoff_time = datetime.now() - duration
            return [usage for usage in self._resource_history if usage.timestamp >= cutoff_time]

    def get_peak_metrics(self) -> Dict[str, float]:
        with self._lock:
            return self._peak_metrics.copy()

    def get_critical_events(self, duration: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        with self._lock:
            if not duration:
                return self._critical_events.copy()
            cutoff_time = datetime.now() - duration
            return [event for event in self._critical_events if event['timestamp'] >= cutoff_time]

system_resource_monitor = SystemResourceMonitor()

__all__ = ['SystemResourceMonitor', 'ResourceUsage', 'system_resource_monitor']