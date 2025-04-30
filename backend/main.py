import os
import sys
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from core.config import settings
from core.sentry import configure_sentry, capture_exception
from core.plugin_manager import PluginManager
from core.events import startup_events, shutdown_events
from db.database import async_init_db, async_cleanup_db

from api import (
    mods,
    automation,
    settings as settings_router,
    system,
    plugins
)
from api.system.processes import router as advanced_processes_router


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
            self.system_status['database'] = True
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.system_status['database'] = False
            capture_exception(e, "Database initialization failed")
            self.logger.error(f"Database initialization error: {str(e)}")
            raise

    def load_plugins(self) -> None:
        try:
            discovered_plugins = self.plugin_manager.discover_plugins()
            self.plugin_manager.load_all_plugins()
            self.system_status['plugins'] = True
            self.logger.info(f"Loaded {len(discovered_plugins)} plugins successfully")
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
                self.load_plugins()
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

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.get_cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

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

        for router in [
            (mods.router, "/api/mods", ["mods"]),
            (automation.router, "/api/automation", ["automation"]),
            (settings_router.router, "/api/settings", ["settings"]),
            (system.router, "/api/system", ["system"]),
            (advanced_processes_router, "/api/system", ["advanced_processes"]),
            (plugins.router, "/api/plugins", ["plugins"])
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
        workers=getattr(settings, "WORKERS", 1)
    )
