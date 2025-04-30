from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict
from core.process_management.advanced_monitor import AdvancedProcessMonitor, ProcessInfo

router = APIRouter(
    prefix="/advanced-processes",
    tags=["advanced_processes"]
)

process_monitor = AdvancedProcessMonitor()

@router.get("/", response_model=List[Dict])
async def get_all_processes(
    tag: Optional[str] = Query(None, description="Filter processes by tag"),
    min_cpu_usage: Optional[float] = Query(None, ge=0, le=100, description="Minimum CPU usage threshold"),
    min_memory_usage: Optional[float] = Query(None, ge=0, le=100, description="Minimum memory usage threshold")
) -> List[Dict]:
    if not process_monitor.is_monitoring():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Process monitoring service is not active"
        )
        
    try:
        processes = process_monitor.get_processes_by_tag(tag) if tag else process_monitor.get_all_processes()
        
        filtered_processes = [
            p for p in processes
            if (min_cpu_usage is None or p.cpu_usage >= min_cpu_usage) and
               (min_memory_usage is None or p.memory_usage >= min_memory_usage)
        ]
        
        return [
            {
                "pid": p.pid,
                "name": p.name,
                "exe_path": p.exe_path,
                "start_time": p.start_time.isoformat() if p.start_time else None,
                "cpu_usage": round(p.cpu_usage, 2),
                "memory_usage": round(p.memory_usage, 2),
                "status": p.status,
                "tags": sorted(list(p.tags)) if p.tags else [],
                "threads_count": p.threads_count
            } 
            for p in filtered_processes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/by-tag/{tag}", response_model=List[Dict])
async def get_processes_by_tag(tag: str) -> List[Dict]:
    if not tag.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag parameter cannot be empty"
        )
        
    if not process_monitor.is_monitoring():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Process monitoring service is not active"
        )
        
    try:
        processes = process_monitor.get_processes_by_tag(tag.strip())
        return [
            {
                "pid": p.pid,
                "name": p.name,
                "exe_path": p.exe_path,
                "cpu_usage": round(p.cpu_usage, 2),
                "memory_usage": round(p.memory_usage, 2),
                "tags": sorted(list(p.tags)) if p.tags else []
            } 
            for p in processes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/start-monitoring", status_code=status.HTTP_200_OK)
async def start_process_monitoring() -> Dict[str, str]:
    if process_monitor.is_monitoring():
        return {"status": "Process monitoring is already running"}
        
    try:
        process_monitor.start_monitoring()
        return {"status": "Process monitoring started successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/stop-monitoring", status_code=status.HTTP_200_OK)
async def stop_process_monitoring() -> Dict[str, str]:
    if not process_monitor.is_monitoring():
        return {"status": "Process monitoring is already stopped"}
        
    try:
        process_monitor.stop_monitoring()
        return {"status": "Process monitoring stopped successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )