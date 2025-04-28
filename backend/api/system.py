from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import psutil
import os
import platform
from datetime import datetime

from core.process_monitor.monitor import ProcessMonitor
from core.system_info import get_system_info, get_running_processes, get_resource_usage

router = APIRouter(
    prefix="/system",
    tags=["system"],
)

process_monitor = ProcessMonitor()

@router.get("/info")
async def system_information():
    """Get basic system information"""
    return get_system_info()

@router.get("/processes")
async def running_processes(limit: int = 20):
    """Get list of running processes sorted by CPU usage"""
    return get_running_processes(limit)

@router.get("/resources")
async def resource_usage():
    """Get current system resource usage"""
    return get_resource_usage()

@router.get("/monitored-processes")
async def get_monitored_processes():
    """Get list of processes being monitored"""
    return process_monitor.get_monitored_processes()

@router.post("/monitor-process/{process_name}")
async def add_monitored_process(process_name: str, background_tasks: BackgroundTasks):
    """Add a process to the monitoring list"""
    # Check if process exists
    process_exists = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == process_name.lower():
            process_exists = True
            break
    
    if not process_exists:
        raise HTTPException(status_code=404, detail=f"Process '{process_name}' not found running on the system")
    
    # Add to monitor
    background_tasks.add_task(process_monitor.add_process, process_name)
    return {"detail": f"Process '{process_name}' added to monitoring"}

@router.delete("/monitor-process/{process_name}")
async def remove_monitored_process(process_name: str):
    """Remove a process from the monitoring list"""
    if not process_monitor.is_monitored(process_name):
        raise HTTPException(status_code=404, detail=f"Process '{process_name}' is not being monitored")
    
    process_monitor.remove_process(process_name)
    return {"detail": f"Process '{process_name}' removed from monitoring"}

@router.get("/active-apps")
async def get_active_applications():
    """Get list of active/focused applications"""
    return process_monitor.get_active_applications()

@router.post("/restart-service")
async def restart_service(background_tasks: BackgroundTasks):
    """Restart the DesktopMods service"""
    # This would typically call a script or service manager to restart the app
    background_tasks.add_task(restart_app_service)
    return {"detail": "Service restart initiated"}

def restart_app_service():
    """Background task to restart the service"""
    # Implement platform-specific service restart logic
    # This is just a placeholder - would need actual implementation
    import time
    time.sleep(1)  # Simulate restart delay
    # In a real application, this might call systemctl, Windows Service API, etc.
    return True