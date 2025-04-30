# Amélioration dans backend/api/health.py

from fastapi import APIRouter, status, Response, Depends
from pydantic import BaseModel
from typing import Dict, Optional, List
import platform
import time
import logging
import psutil
import os
from pathlib import Path

router = APIRouter(tags=["health"])

class ServiceStatus(BaseModel):
    name: str
    status: str
    details: Optional[Dict] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
    hostname: str
    timestamp: float
    environment: Optional[str] = None
    database_status: str
    services: List[ServiceStatus]

# Track when the service started
START_TIME = time.time()

logger = logging.getLogger(__name__)


def check_database_connection():
    try:
        from db.database import db_session
        from sqlalchemy import text
        
        with db_session() as session:
            # Use text() to explicitly declare the SQL statement
            session.execute(text("SELECT 1")).scalar()
            return "ok"
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return "error"

def check_file_system():
    try:
        # Vérifier les permissions d'écriture dans le répertoire de données
        from core.config import settings
        data_dir = Path(settings.DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Test d'écriture
        test_file = data_dir / ".healthcheck"
        test_file.write_text("test")
        test_file.unlink()  # Supprimer le fichier de test
        
        return {"status": "ok", "data_dir": str(data_dir)}
    except Exception as e:
        logger.error(f"File system check failed: {e}")
        return {"status": "error", "error": str(e)}

def check_resource_monitor():
    try:
        from core.resource_monitor import system_resource_monitor
        
        status = "ok" if system_resource_monitor.is_monitoring() else "inactive"
        
        metrics = None
        try:
            latest = system_resource_monitor.get_latest_usage()
            if latest:
                metrics = {
                    "cpu": round(latest.cpu_percent, 1),
                    "memory": round(latest.memory_usage, 1),
                    "disk": round(latest.disk_usage, 1)
                }
        except Exception as e:
            logger.warning(f"Could not get resource metrics: {e}")
        
        return {"status": status, "metrics": metrics}
    except Exception as e:
        logger.error(f"Resource monitor check failed: {e}")
        return {"status": "error", "error": str(e)}

def check_process_monitor():
    try:
        from core.process_management.advanced_monitor import advanced_process_monitor
        
        status = "ok" if advanced_process_monitor.is_monitoring() else "inactive"
        
        process_count = 0
        try:
            processes = advanced_process_monitor.get_all_processes()
            process_count = len(processes)
        except Exception as e:
            logger.warning(f"Could not get process count: {e}")
        
        return {"status": status, "process_count": process_count}
    except Exception as e:
        logger.error(f"Process monitor check failed: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(detailed: bool = False, response: Response = None) -> Dict:
    logger.info("Health check endpoint accessed")
    
    # Check database connection
    db_status = check_database_connection()
    
    # Create service status list
    services = [
        ServiceStatus(
            name="database",
            status=db_status,
            details={"type": os.environ.get("MODHUB_DB_TYPE", "sqlite")}
        )
    ]
    
    # Vérifier si une vérification détaillée est demandée
    if detailed:
        # Check file system
        fs_check = check_file_system()
        services.append(ServiceStatus(
            name="filesystem",
            status=fs_check.get("status", "error"),
            details=fs_check
        ))
        
        # Check resource monitor
        resource_check = check_resource_monitor()
        services.append(ServiceStatus(
            name="resource_monitor",
            status=resource_check.get("status", "error"),
            details=resource_check
        ))
        
        # Check process monitor
        process_check = check_process_monitor()
        services.append(ServiceStatus(
            name="process_monitor",
            status=process_check.get("status", "error"),
            details=process_check
        ))
    
    # Determine overall status
    overall_status = "ok"
    if any(service.status == "error" for service in services):
        overall_status = "error"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif any(service.status != "ok" for service in services):
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "version": "0.1.0",
        "uptime": time.time() - START_TIME,
        "hostname": platform.node(),
        "timestamp": time.time(),
        "environment": os.environ.get("MODHUB_ENVIRONMENT", "development"),
        "database_status": db_status,
        "services": services
    }

# Add a more detailed health check endpoint
@router.get("/health/detailed", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def detailed_health_check(response: Response = None) -> Dict:
    return await health_check(detailed=True, response=response)

# Add a simple liveness probe that doesn't check dependencies
@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_probe() -> Dict:
    return {
        "status": "alive",
        "uptime": time.time() - START_TIME
    }