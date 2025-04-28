import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import mods, automation as process_monitor, settings, system
from core.process_monitor import ProcessMonitor
from core.config import settings as app_settings

app = FastAPI(
    title="ModHub Central API",
    description="Backend API for ModHub Central - Hub Centralisé de Gestion de Mods PC",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "electron://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(mods.router, prefix="/api/mods", tags=["mods"])
app.include_router(process_monitor.router, prefix="/api/monitor", tags=["monitor"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

# Initialize process monitor on startup
@app.on_event("startup")
async def startup_event():
    global monitor
    monitor = ProcessMonitor()
    print("✅ ProcessMonitor initialized (no await needed).")


@app.get("/")
async def root():
    return {"message": "Welcome to ModHub Central API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=app_settings.HOST, port=app_settings.PORT, reload=True)