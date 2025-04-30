from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any

from .processes import router as processes_router
from .resources import router as resources_router
from core.resource_monitor import system_resource_monitor
from core.process_management.advanced_monitor import advanced_process_monitor

router = APIRouter(prefix="/system", tags=["system"])

# Inclure les sous-routeurs
router.include_router(processes_router)
router.include_router(resources_router)

@router.get("/info", response_model=Dict[str, Any])
async def get_system_info() -> Dict[str, Any]:
    """Obtenir des informations de base sur le système"""
    try:
        # Importer depuis le bon module
        from ..system_info import get_system_info
        return get_system_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_info() -> Dict[str, Any]:
    """Obtenir des informations complètes pour le tableau de bord"""
    try:
        # Démarrer les moniteurs si nécessaire
        if not system_resource_monitor.is_monitoring():
            system_resource_monitor.start_monitoring()
        
        if not advanced_process_monitor.is_monitoring():
            advanced_process_monitor.start_monitoring()
            
        # Obtenir les ressources actuelles
        latest_resources = system_resource_monitor.get_latest_usage()
        resource_peaks = system_resource_monitor.get_peak_metrics()
        
        # Obtenir les processus importants
        all_processes = advanced_process_monitor.get_all_processes()
        high_cpu_processes = sorted(
            [p for p in all_processes if p.cpu_usage > 5.0],
            key=lambda p: p.cpu_usage,
            reverse=True
        )[:5]
        
        high_memory_processes = sorted(
            [p for p in all_processes if p.memory_usage > 1.0],
            key=lambda p: p.memory_usage,
            reverse=True
        )[:5]
        
        # Construire la réponse
        return {
            "resources": {
                "cpu": round(latest_resources.cpu_percent, 1),
                "memory": round(latest_resources.memory_usage, 1),
                "disk": round(latest_resources.disk_usage, 1),
                "peaks": {
                    "cpu": round(resource_peaks.get('cpu_peak', 0.0), 1),
                    "memory": round(resource_peaks.get('memory_peak', 0.0), 1),
                    "disk": round(resource_peaks.get('disk_peak', 0.0), 1)
                }
            },
            "processes": {
                "total_count": len(all_processes),
                "high_cpu": [
                    {"pid": p.pid, "name": p.name, "cpu": round(p.cpu_usage, 1), "memory": round(p.memory_usage, 1)}
                    for p in high_cpu_processes
                ],
                "high_memory": [
                    {"pid": p.pid, "name": p.name, "cpu": round(p.cpu_usage, 1), "memory": round(p.memory_usage, 1)}
                    for p in high_memory_processes
                ]
            },
            "system_status": {
                "resource_monitoring_active": system_resource_monitor.is_monitoring(),
                "process_monitoring_active": advanced_process_monitor.is_monitoring()
            },
            "timestamp": latest_resources.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-monitoring", response_model=Dict[str, Any])
async def start_all_monitoring() -> Dict[str, Any]:
    """Démarrer tous les systèmes de surveillance"""
    resource_result = False
    process_result = False
    
    try:
        if not system_resource_monitor.is_monitoring():
            resource_result = system_resource_monitor.start_monitoring()
        else:
            resource_result = True
    except Exception as e:
        resource_result = False
    
    try:
        if not advanced_process_monitor.is_monitoring():
            process_result = advanced_process_monitor.start_monitoring()
        else:
            process_result = True
    except Exception as e:
        process_result = False
    
    return {
        "resource_monitoring": "started" if resource_result else "failed",
        "process_monitoring": "started" if process_result else "failed",
        "all_success": resource_result and process_result
    }

@router.post("/stop-monitoring", response_model=Dict[str, Any])
async def stop_all_monitoring() -> Dict[str, Any]:
    """Arrêter tous les systèmes de surveillance"""
    resource_result = False
    process_result = False
    
    try:
        if system_resource_monitor.is_monitoring():
            resource_result = system_resource_monitor.stop_monitoring()
        else:
            resource_result = True
    except Exception as e:
        resource_result = False
    
    try:
        if advanced_process_monitor.is_monitoring():
            process_result = advanced_process_monitor.stop_monitoring()
        else:
            process_result = True
    except Exception as e:
        process_result = False
    
    return {
        "resource_monitoring": "stopped" if resource_result else "failed",
        "process_monitoring": "stopped" if process_result else "failed",
        "all_success": resource_result and process_result
    }