from fastapi import APIRouter, HTTPException
from typing import Dict, List, TypedDict
import platform
import psutil
import socket

class SystemInfo(TypedDict):
    os: str
    version: str
    hostname: str
    cpu_count: int
    memory_total: int

class ProcessInfo(TypedDict):
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float

class ResourceUsage(TypedDict):
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    network_io: Dict[str, int]

router = APIRouter(prefix="/system", tags=["system"])

async def get_system_info() -> SystemInfo:
    return {
        "os": platform.system(),
        "version": platform.version(),
        "hostname": socket.gethostname(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total
    }

async def get_running_processes() -> List[ProcessInfo]:
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        try:
            process_info = {
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "status": proc.info['status'],
                "cpu_percent": proc.cpu_percent(),
                "memory_percent": proc.memory_percent()
            }
            processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

async def get_resource_usage() -> ResourceUsage:
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        },
        "network_io": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv
        }
    }

@router.get("/info", response_model=SystemInfo)
async def system_info() -> SystemInfo:
    try:
        return await get_system_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processes", response_model=List[ProcessInfo])
async def running_processes() -> List[ProcessInfo]:
    try:
        return await get_running_processes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resources", response_model=ResourceUsage)
async def resource_usage() -> ResourceUsage:
    try:
        return await get_resource_usage()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))