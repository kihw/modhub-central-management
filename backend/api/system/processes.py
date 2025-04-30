from fastapi import APIRouter, HTTPException, Query, status, Response, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, conint, confloat

from core.process_management.advanced_monitor import advanced_process_monitor, ProcessInfo
from core.process_monitor import process_monitor as simple_process_monitor

router = APIRouter(
    prefix="/advanced-processes",
    tags=["advanced_processes"]
)

class ProcessBase(BaseModel):
    pid: int
    name: str
    status: str = "unknown"

class ProcessDetail(ProcessBase):
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    exe_path: Optional[str] = None
    threads_count: Optional[int] = None
    tags: List[str] = []
    io_read_bytes: Optional[int] = None
    io_write_bytes: Optional[int] = None
    is_monitored: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "pid": 1234,
                "name": "chrome.exe",
                "status": "running",
                "cpu_usage": 2.5,
                "memory_usage": 5.8,
                "exe_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "threads_count": 32,
                "tags": ["browser"],
                "io_read_bytes": 1234567,
                "io_write_bytes": 654321,
                "is_monitored": False
            }
        }

class MonitoringStatusResponse(BaseModel):
    status: str
    processes_count: int
    high_cpu_processes: int
    high_memory_processes: int
    monitored_processes: int
    scan_interval: float

def _process_info_to_detail(p: ProcessInfo) -> ProcessDetail:
    """Convertir ProcessInfo en ProcessDetail Pydantic"""
    return ProcessDetail(
        pid=p.pid,
        name=p.name,
        status=p.status,
        cpu_usage=round(p.cpu_usage, 2),
        memory_usage=round(p.memory_usage, 2),
        exe_path=p.exe_path,
        threads_count=p.threads_count,
        tags=list(p.tags) if p.tags else [],
        io_read_bytes=p.io_read_bytes,
        io_write_bytes=p.io_write_bytes,
        is_monitored=p.is_monitored
    )

@router.get("/", response_model=List[ProcessDetail])
async def get_all_processes(
    tag: Optional[str] = Query(None, description="Filter processes by tag"),
    min_cpu_usage: Optional[float] = Query(None, ge=0, le=100, description="Minimum CPU usage threshold"),
    min_memory_usage: Optional[float] = Query(None, ge=0, le=100, description="Minimum memory usage threshold"),
    limit: Optional[int] = Query(50, ge=1, le=500, description="Maximum number of processes to return")
) -> List[Dict]:
    if not advanced_process_monitor.is_monitoring():
        # Essayer de démarrer si ce n'est pas déjà en cours
        success = advanced_process_monitor.start_monitoring()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Process monitoring service failed to start"
            )
        
    try:
        # Obtenir les processus avec filtres
        if tag:
            processes = advanced_process_monitor.get_processes_by_tag(tag)
        else:
            processes = advanced_process_monitor.get_all_processes()
        
        # Filtrer par utilisation CPU/mémoire
        filtered_processes = [
            p for p in processes
            if (min_cpu_usage is None or p.cpu_usage >= min_cpu_usage) and
               (min_memory_usage is None or p.memory_usage >= min_memory_usage)
        ]
        
        # Trier par utilisation CPU (décroissant)
        sorted_processes = sorted(filtered_processes, key=lambda p: p.cpu_usage, reverse=True)
        
        # Limiter le nombre de résultats
        limited_processes = sorted_processes[:limit]
        
        # Convertir en modèle Pydantic
        return [_process_info_to_detail(p) for p in limited_processes]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/by-tag/{tag}", response_model=List[ProcessDetail])
async def get_processes_by_tag(tag: str) -> List[Dict]:
    if not tag.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag parameter cannot be empty"
        )
        
    if not advanced_process_monitor.is_monitoring():
        # Essayer de démarrer si ce n'est pas déjà en cours
        advanced_process_monitor.start_monitoring()
        
    try:
        processes = advanced_process_monitor.get_processes_by_tag(tag.strip())
        return [_process_info_to_detail(p) for p in processes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/by-name/{name}", response_model=List[ProcessDetail])
async def get_processes_by_name(name: str) -> List[Dict]:
    if not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name parameter cannot be empty"
        )
        
    if not advanced_process_monitor.is_monitoring():
        advanced_process_monitor.start_monitoring()
        
    try:
        processes = advanced_process_monitor.get_process_by_name(name.strip())
        return [_process_info_to_detail(p) for p in processes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_process_stats() -> Dict[str, Any]:
    if not advanced_process_monitor.is_monitoring():
        advanced_process_monitor.start_monitoring()
        
    try:
        return advanced_process_monitor.get_process_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/start-monitoring", status_code=status.HTTP_200_OK)
async def start_process_monitoring() -> Dict[str, str]:
    if advanced_process_monitor.is_monitoring():
        return {"status": "Process monitoring is already running"}
        
    try:
        success = advanced_process_monitor.start_monitoring()
        if success:
            return {"status": "Process monitoring started successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start process monitoring"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/stop-monitoring", status_code=status.HTTP_200_OK)
async def stop_process_monitoring() -> Dict[str, str]:
    if not advanced_process_monitor.is_monitoring():
        return {"status": "Process monitoring is already stopped"}
        
    try:
        success = advanced_process_monitor.stop_monitoring()
        if success:
            return {"status": "Process monitoring stopped successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop process monitoring"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/status", response_model=MonitoringStatusResponse)
async def get_monitoring_status() -> MonitoringStatusResponse:
    try:
        is_running = advanced_process_monitor.is_monitoring()
        all_processes = advanced_process_monitor.get_all_processes()
        high_cpu = [p for p in all_processes if p.cpu_usage > 70]
        high_memory = [p for p in all_processes if p.memory_usage > 70]
        
        return MonitoringStatusResponse(
            status="running" if is_running else "stopped",
            processes_count=len(all_processes),
            high_cpu_processes=len(high_cpu),
            high_memory_processes=len(high_memory),
            monitored_processes=len(advanced_process_monitor._monitored_callbacks),
            scan_interval=advanced_process_monitor._scan_interval
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Route pour le moniteur de processus simple
@router.get("/simple", tags=["simple_processes"])
async def get_simple_monitored_processes() -> Dict[str, Any]:
    if not simple_process_monitor.is_monitoring:
        simple_process_monitor.start_monitoring()
        
    try:
        running_processes = simple_process_monitor.get_running_processes()
        watched_processes = list(simple_process_monitor.watched_processes.keys())
        
        result = {
            "running_processes": running_processes,
            "watched_processes": watched_processes,
            "count": len(running_processes),
            "watched_count": len(watched_processes),
            "is_monitoring": simple_process_monitor.is_monitoring,
            "scan_interval": simple_process_monitor.get_scan_interval()
        }
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )