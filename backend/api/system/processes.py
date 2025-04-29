"""
Advanced Process Management API Routes
Provides comprehensive process monitoring and management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from core.process_management.advanced_monitor import AdvancedProcessMonitor, ProcessInfo

router = APIRouter(
    prefix="/advanced-processes",
    tags=["advanced_processes"]
)

# Global process monitor instance
process_monitor = AdvancedProcessMonitor()

@router.get("/")
async def get_all_processes(
    tag: Optional[str] = Query(None, description="Filter processes by tag"),
    min_cpu_usage: Optional[float] = Query(None, description="Minimum CPU usage threshold"),
    min_memory_usage: Optional[float] = Query(None, description="Minimum memory usage threshold")
) -> List[dict]:
    """
    Retrieve comprehensive process information with optional filtering
    
    Parameters:
    - tag: Filter processes by a specific tag (e.g., 'gaming', 'media')
    - min_cpu_usage: Filter processes by minimum CPU usage percentage
    - min_memory_usage: Filter processes by minimum memory usage percentage
    """
    processes = process_monitor.get_processes_by_tag(tag) if tag else list(process_monitor._tracked_processes.values())
    
    filtered_processes = [
        p for p in processes
        if ((min_cpu_usage is None or p.cpu_usage >= min_cpu_usage) and
            (min_memory_usage is None or p.memory_usage >= min_memory_usage))
    ]
    
    return [
        {
            "pid": p.pid,
            "name": p.name,
            "exe_path": p.exe_path,
            "start_time": p.start_time,
            "cpu_usage": p.cpu_usage,
            "memory_usage": p.memory_usage,
            "status": p.status,
            "tags": p.tags,
            "threads_count": p.threads_count
        } 
        for p in filtered_processes
    ]

@router.get("/by-tag/{tag}")
async def get_processes_by_tag(tag: str) -> List[dict]:
    """
    Retrieve processes with a specific tag
    
    Parameters:
    - tag: Process tag to filter (e.g., 'gaming', 'media', 'development')
    """
    processes = process_monitor.get_processes_by_tag(tag)
    
    return [
        {
            "pid": p.pid,
            "name": p.name,
            "exe_path": p.exe_path,
            "cpu_usage": p.cpu_usage,
            "memory_usage": p.memory_usage,
            "tags": p.tags
        } 
        for p in processes
    ]

@router.post("/start-monitoring")
async def start_process_monitoring():
    """Start advanced process monitoring"""
    try:
        process_monitor.start_monitoring()
        return {"status": "Monitoring started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-monitoring")
async def stop_process_monitoring():
    """Stop advanced process monitoring"""
    try:
        process_monitor.stop_monitoring()
        return {"status": "Monitoring stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))