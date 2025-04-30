# Dans backend/core/system_info.py
import os
import psutil
import platform
from typing import Any, Dict, List, Optional
import logging
from pathlib import Path
import time
from datetime import datetime

logger = logging.getLogger(__name__)

def get_system_info() -> Dict[str, float]:
    """Obtenir des informations de base sur le système"""
    try:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(str(Path.home()))
        cpu_count_physical = psutil.cpu_count(logical=False) or 0
        cpu_count_logical = psutil.cpu_count(logical=True) or 0
        
        system_info = {
            "cpu_count_physical": cpu_count_physical,
            "cpu_count_logical": cpu_count_logical,
            "memory_total": float(vm.total),
            "memory_available": float(vm.available),
            "disk_total": float(disk.total),
            "disk_free": float(disk.free),
            "boot_time": float(psutil.boot_time()),
            "hostname": platform.node(),
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "timestamp": time.time()
        }
        return system_info
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        # Retourner des valeurs par défaut en cas d'erreur
        return {
            "cpu_count_physical": 0,
            "cpu_count_logical": 0,
            "memory_total": 0.0,
            "memory_available": 0.0,
            "disk_total": 0.0,
            "disk_free": 0.0,
            "boot_time": 0.0,
            "hostname": "unknown",
            "os_name": platform.system(),
            "os_version": "unknown",
            "os_release": "unknown",
            "python_version": platform.python_version(),
            "timestamp": time.time()
        }

def get_running_processes() -> List[Dict[str, float]]:
    """Obtenir la liste des processus en cours d'exécution"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'memory_percent', 'cpu_percent', 'status'])
                pinfo['memory_percent'] = float(pinfo.get('memory_percent') or 0)
                pinfo['cpu_percent'] = float(pinfo.get('cpu_percent') or 0)
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            
        # Trier par utilisation CPU (décroissant)
        processes.sort(key=lambda p: p.get('cpu_percent', 0), reverse=True)
        return processes
    except Exception as e:
        logger.error(f"Error getting running processes: {e}")
        return []

def get_resource_usage() -> Dict[str, float]:
    """Obtenir l'utilisation actuelle des ressources système"""
    try:
        # Mémoire
        vm = psutil.virtual_memory()
        
        # Disque
        try:
            disk = psutil.disk_usage(str(Path.home()))
        except Exception:
            # Utiliser la racine si le répertoire home pose problème
            try:
                disk = psutil.disk_usage('/')
            except Exception:
                # Valeurs par défaut si impossible d'obtenir l'utilisation du disque
                class DummyDisk:
                    def __init__(self):
                        self.total = 0
                        self.used = 0
                        self.free = 0
                        self.percent = 0.0
                disk = DummyDisk()
        
        # CPU
        try:
            cpu_freq = psutil.cpu_freq()
            current_freq = cpu_freq.current if cpu_freq else 0
        except Exception:
            current_freq = 0
            
        # Swap
        try:
            swap = psutil.swap_memory()
            swap_percent = swap.percent
        except Exception:
            swap_percent = 0.0
            
        resource_usage = {
            "cpu_percent": float(psutil.cpu_percent(interval=0.1)),
            "cpu_freq": float(current_freq),
            "memory_percent": float(vm.percent),
            "memory_used": float(vm.used),
            "memory_available": float(vm.available),
            "swap_percent": float(swap_percent),
            "disk_usage": float(disk.percent),
            "disk_used": float(disk.used),
            "disk_free": float(disk.free),
            "timestamp": time.time()
        }
        return resource_usage
    except Exception as e:
        logger.error(f"Error getting resource usage: {e}")
        # Retourner des valeurs par défaut en cas d'erreur
        return {
            "cpu_percent": 0.0,
            "cpu_freq": 0.0,
            "memory_percent": 0.0,
            "memory_used": 0.0,
            "memory_available": 0.0,
            "swap_percent": 0.0,
            "disk_usage": 0.0,
            "disk_used": 0.0, 
            "disk_free": 0.0,
            "timestamp": time.time()
        }

def get_detailed_system_info() -> Dict[str, Any]:
    """Obtenir des informations détaillées sur le système"""
    basic_info = get_system_info()
    resource_usage = get_resource_usage()
    top_processes = get_running_processes()[:5]  # Top 5 processus CPU
    
    # Information réseau
    try:
        net_io = psutil.net_io_counters()
        network = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    except Exception:
        network = {
            "bytes_sent": 0,
            "bytes_recv": 0,
            "packets_sent": 0,
            "packets_recv": 0
        }
    
    # Uptime
    try:
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        uptime = {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": uptime_seconds
        }
    except Exception:
        uptime = {
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "seconds": 0,
            "total_seconds": 0
        }
    
    return {
        "system": basic_info,
        "resources": resource_usage,
        "top_processes": top_processes,
        "network": network,
        "uptime": uptime,
        "timestamp": datetime.now().isoformat()
    }