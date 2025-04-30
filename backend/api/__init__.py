from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
import psutil
import yaml
from pathlib import Path
from datetime import datetime
import asyncio
import logging
from contextlib import asynccontextmanager

class ModType(str, Enum):
    GAMING = "gaming"
    NIGHT = "night"
    MEDIA = "media"
    CUSTOM = "custom"

class ModStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class ModConfig(BaseModel):
    name: str
    type: ModType
    enabled: bool = Field(default=False)
    priority: int = Field(ge=0, le=100)
    config: Dict = Field(default_factory=dict)
    conditions: List[Dict] = Field(default_factory=list)
    actions: List[Dict] = Field(default_factory=list)

class ModState(BaseModel):
    mod_id: str
    status: ModStatus = ModStatus.INACTIVE
    active_rules: List[str] = Field(default_factory=list)
    last_trigger: Optional[float] = None
    last_update: float = Field(default_factory=lambda: datetime.now().timestamp())

class ModHub:
    def __init__(self):
        self.mod_configs: Dict[str, ModConfig] = {}
        self.mod_states: Dict[str, ModState] = {}
        self.config_lock = asyncio.Lock()
        self.config_path = Path("config/mods")
        self.config_path.mkdir(parents=True, exist_ok=True)

    async def load_configurations(self):
        for file in self.config_path.glob("*.yaml"):
            try:
                config_data = yaml.safe_load(file.read_text())
                self.mod_configs[file.stem] = ModConfig(**config_data)
                if file.stem not in self.mod_states:
                    self.mod_states[file.stem] = ModState(mod_id=file.stem)
            except Exception as e:
                logging.error(f"Error loading config {file}: {e}")

    async def save_mod_config(self, mod_id: str):
        config_file = self.config_path / f"{mod_id}.yaml"
        async with self.config_lock:
            config_file.write_text(yaml.dump(self.mod_configs[mod_id].dict()))

mod_hub = ModHub()
app = FastAPI(title="ModHub Central API", version="0.1.0")

@app.on_event("startup")
async def startup_event():
    await mod_hub.load_configurations()

@app.get("/api/v1/mods", response_model=Dict[str, ModConfig])
async def get_mods():
    return mod_hub.mod_configs

@app.get("/api/v1/mods/{mod_id}", response_model=ModConfig)
async def get_mod(mod_id: str):
    if mod_id not in mod_hub.mod_configs:
        raise HTTPException(status_code=404, detail="Mod not found")
    return mod_hub.mod_configs[mod_id]

@app.post("/api/v1/mods/{mod_id}/toggle", response_model=ModConfig)
async def toggle_mod(mod_id: str):
    if mod_id not in mod_hub.mod_configs:
        raise HTTPException(status_code=404, detail="Mod not found")
    async with mod_hub.config_lock:
        mod_hub.mod_configs[mod_id].enabled = not mod_hub.mod_configs[mod_id].enabled
        await mod_hub.save_mod_config(mod_id)
    return mod_hub.mod_configs[mod_id]

@app.put("/api/v1/mods/{mod_id}", response_model=ModConfig)
async def update_mod(mod_id: str, config: ModConfig):
    if mod_id not in mod_hub.mod_configs:
        raise HTTPException(status_code=404, detail="Mod not found")
    async with mod_hub.config_lock:
        mod_hub.mod_configs[mod_id] = config
        await mod_hub.save_mod_config(mod_id)
    return config

@app.get("/api/v1/system/processes")
async def get_active_processes() -> List[Dict]:
    try:
        return [proc.info for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent'])]
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return []

@app.get("/api/v1/system/status")
async def get_system_status() -> Dict:
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "active_mods": [mod_id for mod_id, config in mod_hub.mod_configs.items() if config.enabled],
            "mod_states": mod_hub.mod_states,
            "timestamp": datetime.now().timestamp()
        }
    except Exception as e:
        logging.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Error getting system status")

@app.get("/api/v1/mods/{mod_id}/state", response_model=ModState)
async def get_mod_state(mod_id: str):
    if mod_id not in mod_hub.mod_states:
        raise HTTPException(status_code=404, detail="Mod state not found")
    return mod_hub.mod_states[mod_id]

@app.put("/api/v1/mods/{mod_id}/state", response_model=ModState)
async def update_mod_state(mod_id: str, state: ModState):
    state.last_update = datetime.now().timestamp()
    mod_hub.mod_states[mod_id] = state
    return state