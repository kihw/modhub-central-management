from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

# In-memory fake settings storage (à remplacer par base de données plus tard)
fake_settings_db: Dict[str, str] = {
    "theme": "light",
    "notifications_enabled": "true",
    "auto_backup": "false"
}

# Schéma pour mettre à jour un paramètre
class SettingUpdate(BaseModel):
    key: str
    value: str

@router.get("/", response_model=Dict[str, str])
async def get_all_settings():
    """Récupérer tous les paramètres"""
    return fake_settings_db

@router.get("/{key}", response_model=str)
async def get_setting(key: str):
    """Récupérer un paramètre spécifique"""
    if key not in fake_settings_db:
        raise HTTPException(status_code=404, detail="Setting not found")
    return fake_settings_db[key]

@router.put("/", response_model=Dict[str, str])
async def update_setting(update: SettingUpdate):
    """Mettre à jour un paramètre"""
    fake_settings_db[update.key] = update.value
    return fake_settings_db

@router.delete("/{key}", response_model=Dict[str, str])
async def delete_setting(key: str):
    """Supprimer un paramètre"""
    if key not in fake_settings_db:
        raise HTTPException(status_code=404, detail="Setting not found")
    del fake_settings_db[key]
    return fake_settings_db
