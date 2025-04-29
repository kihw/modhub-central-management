"""
ModHub Central API - Backend Service

This is the main entry point for the ModHub Central backend.
It initializes the FastAPI application, sets up routes, and handles 
startup/shutdown events.
"""

import os
import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

# Import routes
from api import mods, automation, settings, system

# Import core components
from core.process_monitor import ProcessMonitor
from core.mods.mod_manager import ModManager
from core.automation.engine import AutomationEngine
from core.config import settings as app_settings

# Import database
from db.database import engine, Base, get_db, init_db
from db import models

# Configure logging
def setup_logging():
    """Configure application logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "modhub.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set lower log level for some noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Set up logger
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="ModHub Central API",
    description="Backend API for ModHub Central - Hub Centralisé de Gestion de Mods PC",
    version="0.1.0"
)

# Add CORS middleware with explicit origin configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Frontend development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances of core components
process_monitor = None
mod_manager = None
automation_engine = None

# Exception handler for uncaught exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log errors and return proper responses"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

# Include routes
app.include_router(mods.router, prefix="/api/mods", tags=["mods"])
app.include_router(automation.router, prefix="/api/automation", tags=["automation"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": time.time()
    }

@app.on_event("startup")
async def startup_event():
    """Initialize components on application startup"""
    global process_monitor, mod_manager, automation_engine
    
    logger.info("Starting ModHub Central backend service")
    
    # Initialize database
    logger.info("Initializing database")
    init_db()
    
    # Initialize process monitor
    logger.info("Initializing process monitor")
    process_monitor = ProcessMonitor()
    
    # Initialize mod manager
    logger.info("Initializing mod manager")
    mod_manager = ModManager()
    
    # Initialize automation engine
    logger.info("Initializing automation engine")
    automation_engine = AutomationEngine(mod_manager=mod_manager)
    
    # Start monitoring and automation
    logger.info("Starting background services")
    automation_engine.start(interval=2.0)  # Check rules every 2 seconds
    
    logger.info("ModHub Central backend service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    global process_monitor, mod_manager, automation_engine
    
    logger.info("Shutting down ModHub Central backend service")
    
    # Stop automation engine
    if automation_engine:
        logger.info("Stopping automation engine")
        automation_engine.stop()
    
    # Additional cleanup as needed
    logger.info("ModHub Central backend service shutdown complete")

@app.get("/")
async def root():
    """Root endpoint, provides basic information"""
    return {
        "name": "ModHub Central API",
        "version": "0.1.0",
        "status": "running",
        "docs_url": "/docs"
    }

# Add a direct status endpoint for frontend health checks
@app.get("/api/status")
async def api_status():
    """API status endpoint for frontend health checks"""
    return {
        "status": "online",
        "version": "0.1.0",
        "services": {
            "processScan": True if process_monitor else False,
            "modEngine": True if mod_manager else False,
            "automation": True if automation_engine else False
        },
        "uptime": time.time()
    }

if __name__ == "__main__":
    # Run the application with uvicorn when executed directly
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Bind to all interfaces
        port=8668,
        reload=True if app_settings.DEBUG else False,
        log_level="info"
    )
