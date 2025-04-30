from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Optional
import platform
import time

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
    hostname: str
    timestamp: float
    environment: Optional[str] = None

# Track when the service started
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> Dict:
    """
    Simple health check endpoint that returns basic service information.
    This serves as both a health check and a CORS test point for frontend apps.
    """
    return {
        "status": "ok",
        "version": "0.1.0",
        "uptime": time.time() - START_TIME,
        "hostname": platform.node(),
        "timestamp": time.time(),
        "environment": "development"
    }
