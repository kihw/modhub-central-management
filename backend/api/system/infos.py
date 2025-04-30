import psutil
from typing import Dict, List, Union
from pathlib import Path

def get_system_info() -> Dict[str, int]:
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(Path.home()))
        return {
            "cpu_count": psutil.cpu_count(logical=True) or 0,
            "cpu_count_physical": psutil.cpu_count(logical=False) or 0,
            "total_memory": memory.total,
            "available_memory": memory.available,
            "total_disk": disk.total,
            "available_disk": disk.free
        }
    except (psutil.Error, OSError):
        return dict.fromkeys([
            "cpu_count", "cpu_count_physical", "total_memory",
            "available_memory", "total_disk", "available_disk"
        ], 0)

def get_running_processes() -> List[Dict[str, Union[int, str, float]]]:
    required_fields = {'pid', 'name', 'username', 'memory_percent'}
    processes = []
    
    try:
        for proc in psutil.process_iter(required_fields):
            try:
                process_info = proc.info
                if all(process_info.get(field) is not None for field in required_fields):
                    processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return sorted(processes, key=lambda x: x.get('memory_percent', 0.0), reverse=True)
    except psutil.Error:
        return []

def get_resource_usage() -> Dict[str, Union[float, List[float]]]:
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(Path.home()))
        swap = psutil.swap_memory()
        
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        per_cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        
        return {
            "cpu_percent": cpu_percent,
            "per_cpu_percent": per_cpu_percent,
            "memory_percent": memory.percent,
            "memory_used": memory.used,
            "disk_percent": disk.percent,
            "disk_used": disk.used,
            "swap_percent": swap.percent
        }
    except (psutil.Error, OSError):
        return {
            "cpu_percent": 0.0,
            "per_cpu_percent": [],
            "memory_percent": 0.0,
            "memory_used": 0.0,
            "disk_percent": 0.0,
            "disk_used": 0.0,
            "swap_percent": 0.0
        }