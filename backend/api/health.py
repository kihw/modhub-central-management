from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Optional
import platform
import time
import logging

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

logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> Dict:
    logger.info("Health check endpoint accessed")  # Ajoutez ce log
    return {
        "status": "ok",
        "version": "0.1.0",
        "uptime": time.time() - START_TIME,
        "hostname": platform.node(),
        "timestamp": time.time(),
        "environment": "development"
    }