"""
Application Initialization and Configuration Module

Provides comprehensive initialization strategies for ModHub Central,
including dependency injection, configuration management, and 
system readiness checks.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Core system components
from core.config import settings
from core.sentry import configure_sentry, capture_exception
from core.plugin_manager import PluginManager
from core.events import startup_events, shutdown_events

# Database and ORM imports
from db.database import engine, Base, init_db

# Router imports
from api import (
    mods,
    automation,
    settings as settings_router,
    system,
    plugins
)
from api.system.processes import router as advanced_processes_router

class ApplicationInitializer:
    """
    Comprehensive application initialization and configuration manager
    """
    
    def __init__(self):
        # Logging setup
        self.logger = logging.getLogger(__name__)
        
        # Dependency containers
        self.dependencies: Dict[str, Any] = {}
        
        # Plugin management
        self.plugin_manager = PluginManager()
        
        # System readiness tracking
        self.system_status = {
            "database": False,
            "plugins": False,
            "external_services": False
        }
    
    def initialize_logging(self):
        """
        Configure comprehensive logging infrastructure
        """
        # Create logs directory
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=settings.get_log_level(),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'modhub_central.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Configure specific loggers
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
        
        self.logger.info("Logging system initialized")
    
    def initialize_database(self):
        """
        Initialize database with comprehensive setup and validation
        """
        try:
            # Create database tables
            Base.metadata.create_all(bind=engine)
            
            # Perform database health check
            # TODO: Implement more robust database connectivity check
            
            self.system_status['database'] = True
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.system_status['database'] = False
            capture_exception(e, "Database initialization failed")
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def load_plugins(self):
        """
        Discover and load available plugins
        """
        try:
            # Discover plugins
            discovered_plugins = self.plugin_manager.discover_plugins()
            
            # Load all discovered plugins
            self.plugin_manager.load_all_plugins()
            
            self.system_status['plugins'] = True
            self.logger.info(f"Loaded {len(discovered_plugins)} plugins successfully")
        except Exception as e:
            self.system_status['plugins'] = False
            capture_exception(e, "Plugin loading failed")
            self.logger.error(f"Plugin loading error: {e}")
    
    def check_external_services(self):
        """
        Perform readiness checks for external services
        """
        # TODO: Implement external service health checks
        # This could include:
        # - Cloud service connectivity
        # - External API availability
        # - Third-party service status
        
        self.system_status['external_services'] = True
        self.logger.info("External services checked")
    
    def create_application(self) -> FastAPI:
        """
        Create and configure the FastAPI application
        
        Returns:
            Fully configured FastAPI application instance
        """
        # Initialize core systems
        self.initialize_logging()
        
        # Configure Sentry if DSN is available
        if settings.SENTRY_DSN:
            configure_sentry(
                dsn=settings.SENTRY_DSN,
                environment=settings.SENTRY_ENVIRONMENT,
                release=settings.APP_VERSION,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE
            )
        
        # Lifespan management for startup and shutdown events
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """
            Manage application startup and shutdown lifecycle
            """
            try:
                # Initialize critical systems
                self.initialize_database()
                self.load_plugins()
                self.check_external_services()
                
                # Run startup events
                await startup_events()
                
                yield {
                    "system_status": self.system_status,
                    "dependencies": self.dependencies
                }
            finally:
                # Ensure proper shutdown
                await shutdown_events()
        
        # Create FastAPI application
        app = FastAPI(
            title="ModHub Central",
            description="Comprehensive Mod Management Platform",
            version=settings.APP_VERSION,
            lifespan=lifespan,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Configure CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.get_cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Global exception handlers
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Custom validation error handler"""
            errors = exc.errors()
            capture_exception(
                message="Request Validation Error", 
                extra={"errors": errors, "request_path": request.url.path}
            )
            return JSONResponse(
                status_code=422,
                content={
                    "message": "Validation Error",
                    "details": errors
                }
            )
        
        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            """Global HTTP exception handler"""
            capture_exception(
                message=f"HTTP {exc.status_code} Error", 
                extra={
                    "status_code": exc.status_code, 
                    "detail": exc.detail,
                    "request_path": request.url.path
                }
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            )
        
        # Include routers
        app.include_router(mods.router, prefix="/api/mods", tags=["mods"])
        app.include_router(automation.router, prefix="/api/automation", tags=["automation"])
        app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
        app.include_router(system.router, prefix="/api/system", tags=["system"])
        app.include_router(advanced_processes_router, prefix="/api/system", tags=["advanced_processes"])
        app.include_router(plugins.router, prefix="/api/plugins", tags=["plugins"])
        
        # System status endpoint
        @app.get("/system/status", tags=["system"])
        async def get_system_status():
            """
            Retrieve comprehensive system status
            """
            return {
                "version": settings.APP_VERSION,
                "system_status": self.system_status,
                "settings": {
                    key: str(value) 
                    for key, value in settings.dict().items() 
                    if not key.lower().endswith(('password', 'key', 'secret'))
                }
            }
        
        return app

def create_app() -> FastAPI:
    """
    Factory function to create the application instance
    
    Returns:
        Configured FastAPI application
    """
    initializer = ApplicationInitializer()
    return initializer.create_application()

# Application instance
app = create_app()

# Main execution block for direct running
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )