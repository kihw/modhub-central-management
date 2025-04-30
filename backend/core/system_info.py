import psutil
from typing import Dict, List, Optional
import logging
from pathlib import Path
from psutil._common import scpufreq

def get_system_info() -> Dict[str, float]:
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage(str(Path.home()))
    system_info = {
        "cpu_count_physical": psutil.cpu_count(logical=False) or 0,
        "cpu_count_logical": psutil.cpu_count(logical=True) or 0,
        "memory_total": float(vm.total),
        "memory_available": float(vm.available),
        "disk_total": float(disk.total),
        "disk_free": float(disk.free),
        "boot_time": float(psutil.boot_time())
    }
    return system_info

def get_running_processes() -> List[Dict[str, float]]:
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'memory_percent'])
            pinfo['memory_percent'] = float(pinfo['memory_percent'] or 0)
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def get_resource_usage() -> Dict[str, float]:
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage(str(Path.home()))
    cpu_freq: Optional[scpufreq] = psutil.cpu_freq()
    
    resource_usage = {
        "cpu_percent": float(psutil.cpu_percent(interval=0.1)),
        "cpu_freq": float(cpu_freq.current if cpu_freq else 0),
        "memory_percent": float(vm.percent),
        "memory_used": float(vm.used),
        "swap_percent": float(psutil.swap_memory().percent),
        "disk_usage": float(disk.percent)
    }
    return resource_usage