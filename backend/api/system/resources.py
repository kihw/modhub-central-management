from fastapi import APIRouter, HTTPException, Query, Depends, status, Response
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, conint, confloat
from datetime import datetime, timedelta
import time

from core.resource_monitor import system_resource_monitor, ResourceUsage

router = APIRouter(
    prefix="/resources",
    tags=["system_resources"]
)

class ResourceMetrics(BaseModel):
    cpu_percent: float
    memory_usage: float
    memory_total: int
    memory_available: int
    disk_usage: float
    disk_total: int
    disk_free: int
    processes_count: int
    timestamp: datetime

class ResourceHistory(BaseModel):
    data: List[ResourceMetrics]
    count: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ResourcePeaks(BaseModel):
    cpu_peak: float
    memory_peak: float
    disk_peak: float
    gpu_peak: float

class MonitoringStatus(BaseModel):
    is_running: bool
    interval: float
    history_length: int
    critical_thresholds: Dict[str, float]

def _resource_usage_to_metrics(usage: ResourceUsage) -> ResourceMetrics:
    """Convertir ResourceUsage en ResourceMetrics Pydantic"""
    return ResourceMetrics(
        cpu_percent=round(usage.cpu_percent, 1),
        memory_usage=round(usage.memory_usage, 1),
        memory_total=usage.total_memory,
        memory_available=usage.available_memory,
        disk_usage=round(usage.disk_usage, 1),
        disk_total=usage.total_disk,
        disk_free=usage.available_disk,
        processes_count=usage.processes_count,
        timestamp=usage.timestamp
    )

@router.get("/current", response_model=ResourceMetrics)
async def get_current_resources() -> ResourceMetrics:
    try:
        # Démarrer le monitoring si ce n'est pas déjà fait
        if not system_resource_monitor.is_monitoring():
            system_resource_monitor.start_monitoring()
            # Attendre une seconde pour collecter au moins une métrique
            time.sleep(1)
            
        latest = system_resource_monitor.get_latest_usage()
        if latest:
            return _resource_usage_to_metrics(latest)
        else:
            # Collecter manuellement si aucune métrique n'est disponible
            usage = system_resource_monitor._collect_system_metrics()
            return _resource_usage_to_metrics(usage)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=ResourceHistory)
async def get_resource_history(
    duration: Optional[int] = Query(60, description="Duration in minutes to fetch history for"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of data points")
) -> ResourceHistory:
    try:
        # Démarrer le monitoring si ce n'est pas déjà fait
        if not system_resource_monitor.is_monitoring():
            system_resource_monitor.start_monitoring()
            
        # Obtenir l'historique
        if duration:
            history = system_resource_monitor.get_resource_history(
                duration=timedelta(minutes=duration),
                limit=limit
            )
        else:
            history = system_resource_monitor.get_resource_history(limit=limit)
            
        # Convertir les données
        metrics = [_resource_usage_to_metrics(usage) for usage in history]
        
        # Déterminer les timestamps de début et de fin
        start_time = metrics[0].timestamp if metrics else None
        end_time = metrics[-1].timestamp if metrics else None
        
        return ResourceHistory(
            data=metrics,
            count=len(metrics),
            start_time=start_time,
            end_time=end_time
        )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/peaks", response_model=ResourcePeaks)
async def get_resource_peaks() -> ResourcePeaks:
    try:
        peaks = system_resource_monitor.get_peak_metrics()
        return ResourcePeaks(
            cpu_peak=peaks.get('cpu_peak', 0.0),
            memory_peak=peaks.get('memory_peak', 0.0),
            disk_peak=peaks.get('disk_peak', 0.0),
            gpu_peak=peaks.get('gpu_peak', 0.0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/reset-peaks", status_code=status.HTTP_200_OK)
async def reset_resource_peaks() -> Dict[str, str]:
    try:
        system_resource_monitor.reset_peak_metrics()
        return {"status": "Resource peak metrics reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/critical-events", response_model=List[Dict[str, Any]])
async def get_critical_events(
    duration: Optional[int] = Query(1440, description="Duration in minutes to fetch events for (default: 24 hours)")
) -> List[Dict[str, Any]]:
    try:
        if duration:
            events = system_resource_monitor.get_critical_events(
                duration=timedelta(minutes=duration)
            )
        else:
            events = system_resource_monitor.get_critical_events()
            
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/status", response_model=MonitoringStatus)
async def get_monitoring_status() -> MonitoringStatus:
    try:
        return MonitoringStatus(
            is_running=system_resource_monitor.is_monitoring(),
            interval=system_resource_monitor._interval,
            history_length=system_resource_monitor._history_length,
            critical_thresholds=system_resource_monitor._thresholds
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/start", status_code=status.HTTP_200_OK)
async def start_resource_monitoring() -> Dict[str, str]:
    try:
        if system_resource_monitor.is_monitoring():
            return {"status": "Resource monitoring is already running"}
        
        result = system_resource_monitor.start_monitoring()
        if result:
            return {"status": "Resource monitoring started successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start resource monitoring"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_resource_monitoring() -> Dict[str, str]:
    try:
        if not system_resource_monitor.is_monitoring():
            return {"status": "Resource monitoring is already stopped"}
        
        result = system_resource_monitor.stop_monitoring()
        if result:
            return {"status": "Resource monitoring stopped successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop resource monitoring"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/gpu", response_model=List[Dict[str, Any]])
async def get_gpu_metrics() -> List[Dict[str, Any]]:
    try:
        # Démarrer le monitoring si ce n'est pas déjà fait
        if not system_resource_monitor.is_monitoring():
            system_resource_monitor.start_monitoring()
            
        latest = system_resource_monitor.get_latest_usage()
        if latest and latest.gpu_usage:
            return latest.gpu_usage
        else:
            # Collecter manuellement si aucune métrique n'est disponible
            return system_resource_monitor._collect_gpu_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/temperature", response_model=List[Dict[str, Any]])
async def get_temperature_metrics() -> List[Dict[str, Any]]:
    try:
        # Démarrer le monitoring si ce n'est pas déjà fait
        if not system_resource_monitor.is_monitoring():
            system_resource_monitor.start_monitoring()
            
        latest = system_resource_monitor.get_latest_usage()
        if latest and latest.temperature:
            return latest.temperature
        else:
            # Collecter manuellement si aucune métrique n'est disponible
            return system_resource_monitor._collect_temperatures()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )