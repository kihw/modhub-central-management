import os
import sys
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, HTTPException, logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from core.config import settings
from core.sentry import configure_sentry, capture_exception
from core.plugin_manager import PluginManager
from core.events import startup_events, shutdown_events
from db.database import async_init_db, async_cleanup_db, engine, init_db
from sqlalchemy.orm import sessionmaker


from api import (
    mods,
    automation,
    settings as settings_router,
    system,
    plugins,
    health
) 
from api.system.processes import router as advanced_processes_router
from api.system.resources import router as resources_router


class ApplicationInitializer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependencies: Dict[str, Any] = {}
        self.plugin_manager = PluginManager()
        self.system_status = {
            "database": False,
            "plugins": False,
            "external_services": False
        }
        self._app: Optional[FastAPI] = None

    def initialize_logging(self) -> None:
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=settings.get_log_level(),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'modhub_central.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )

        for logger_name in ['sqlalchemy.engine', 'uvicorn.access']:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

        self.logger.info("Logging system initialized")
    async def initialize_database(self) -> None:
        try:
            await async_init_db()

            from db.models import Mod
            session_local = sessionmaker(bind=engine)
            session = session_local()
            try:
                session.query(Mod).first()
                print("Mods table is accessible")
            except Exception as e:
                print(f"Error accessing Mods table: {e}")
                from db.database import manual_db_init
                manual_db_init()
            finally:
                session.close()

            self.system_status['database'] = True
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.system_status['database'] = False
            capture_exception(e, "Database initialization failed")
            self.logger.error(f"Database initialization error: {str(e)}")
            raise

        
    async def load_plugins(self) -> None:
        try:
            discovered_plugins = await self.plugin_manager.discover_plugins()
            plugin_results = await self.plugin_manager.load_all_plugins()
            
            loaded_count = sum(1 for success in plugin_results.values() if success)
            self.system_status['plugins'] = True
            self.logger.info(f"Discovered {len(discovered_plugins)} plugins, loaded {loaded_count} successfully")
        except Exception as e:
            self.system_status['plugins'] = False
            capture_exception(e, "Plugin loading failed")
            self.logger.error(f"Plugin loading error: {str(e)}")

    async def check_external_services(self) -> None:
        try:
            self.system_status['external_services'] = True
            self.logger.info("External services checked")
        except Exception as e:
            self.system_status['external_services'] = False
            capture_exception(e, "External services check failed")
            self.logger.error(f"External services check failed: {str(e)}")

    def create_application(self) -> FastAPI:
        if self._app is not None:
            return self._app

        self.initialize_logging()

        if settings.SENTRY_DSN:
            configure_sentry(
                dsn=settings.SENTRY_DSN,
                environment=settings.SENTRY_ENVIRONMENT,
                release=settings.APP_VERSION,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE
            )

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            try:
                await self.initialize_database()
                await self.load_plugins()
                await self.check_external_services()
                await startup_events()
                yield {"system_status": self.system_status, "dependencies": self.dependencies}
            except Exception as e:
                self.logger.error(f"Application startup failed: {str(e)}")
                raise
            finally:
                try:
                    await shutdown_events()
                    await async_cleanup_db()
                except Exception as e:
                    self.logger.error(f"Application shutdown error: {str(e)}")

        app = FastAPI(
            title="ModHub Central",
            description="Comprehensive Mod Management Platform",
            version=settings.APP_VERSION,
            lifespan=lifespan,
            docs_url="/docs" if settings.DEBUG else None,
            redoc_url="/redoc" if settings.DEBUG else None,
            openapi_url="/openapi.json" if settings.DEBUG else None
        )

        # Enable CORS - this allows frontend applications to connect
        origins = [
            "http://localhost:3000",  # React dev server
            "http://localhost:8000",  # Frontend production/served
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "http://localhost:8668",  # Backend production/served
            "http://127.0.0.1:8668" 
            # Add any other origins that need access
        ]
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.include_router(advanced_processes_router, prefix="/api/system", tags=["advanced_processes"])
        app.include_router(resources_router, prefix="/api/system", tags=["system_resources"])

        # Ajouter un endpoint pour démarrer tous les systèmes de surveillance au démarrage
        @app.on_event("startup")
        async def startup_event():
            # Initialiser la base de données
            await init_db()

            # Démarrer les moniteurs de ressources et de processus
            try:
                from core.resource_monitor import system_resource_monitor
                from core.process_management.advanced_monitor import advanced_process_monitor

                # Démarrer le moniteur de ressources
                system_resource_monitor.start_monitoring()
                logger.info("Resource monitoring started")

                # Démarrer le moniteur de processus
                advanced_process_monitor.start_monitoring()
                logger.info("Process monitoring started")
            except Exception as e:
                logger.error(f"Error starting monitoring systems: {e}")
                
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            capture_exception(exc, extra={"request_path": request.url.path})
            return JSONResponse(
                status_code=422,
                content={"message": "Validation Error", "details": exc.errors()}
            )

        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            capture_exception(exc, extra={"request_path": request.url.path})
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": exc.detail, "status_code": exc.status_code}
            )

        @app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            capture_exception(exc, extra={"request_path": request.url.path})
            return JSONResponse(
                status_code=500,
                content={"message": "Internal Server Error"}
            )

        # Include all routers
        for router in [
            (health.router, "/api", ["health"]),  # Added health router with /api prefix
            (mods.router, "/api", ["mods"]),
            (automation.router, "/api", ["automation"]),
            (settings_router.router, "/api", ["settings"]),
            (system.router, "/api", ["system"]),
            (advanced_processes_router, "/api/system", ["advanced_processes"]),
            (plugins.router, "/api", ["plugins"])
        ]:
            app.include_router(router[0], prefix=router[1], tags=router[2])

        @app.get("/api/status", tags=["system"])
        async def get_system_status():
            return {
                "version": settings.APP_VERSION,
                "system_status": self.system_status,
                "settings": {
                    k: str(v) for k, v in settings.dict().items()
                    if not k.lower().endswith(('password', 'key', 'secret'))
                }
            }

        self._app = app
        return app


def create_app() -> FastAPI:
    return ApplicationInitializer().create_application()


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        workers=settings.WORKERS
    )
