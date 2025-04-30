from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, constr
from typing import Dict, Optional, Any
from enum import Enum

router = APIRouter()

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"

class Language(str, Enum):
    EN = "en"
    FR = "fr"
    DE = "de"
    ES = "es"

DEFAULT_SETTINGS = {
    "theme": Theme.LIGHT,
    "notifications_enabled": "true",
    "auto_backup": "false",
    "language": Language.EN
}

class SettingUpdate(BaseModel):
    key: constr(min_length=1, max_length=50)
    value: constr(min_length=1, max_length=255)

    class Config:
        frozen = True

class SettingsDB:
    def __init__(self):
        self._settings: Dict[str, Any] = DEFAULT_SETTINGS.copy()

    def get_all(self) -> Dict[str, Any]:
        return self._settings.copy()

    def get(self, key: str) -> Any:
        if key not in self._settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting '{key}' not found"
            )
        return self._settings[key]

    def update(self, key: str, value: str) -> Dict[str, Any]:
        if key == "theme" and value not in [t.value for t in Theme]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid theme value"
            )
        if key == "language" and value not in [l.value for l in Language]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid language value"
            )
        if key in ["notifications_enabled", "auto_backup"] and value.lower() not in ["true", "false"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Value must be 'true' or 'false'"
            )
        self._settings[key] = value
        return self.get_all()

    def delete(self, key: str) -> Dict[str, Any]:
        if key not in self._settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting '{key}' not found"
            )
        if key in DEFAULT_SETTINGS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot delete default setting '{key}'"
            )
        del self._settings[key]
        return self.get_all()

settings_db = SettingsDB()

@router.get("/", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_all_settings() -> Dict[str, Any]:
    return settings_db.get_all()

@router.get("/{key}", response_model=Any, status_code=status.HTTP_200_OK)
async def get_setting(key: str) -> Any:
    return settings_db.get(key)

@router.put("/", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def update_setting(update: SettingUpdate) -> Dict[str, Any]:
    return settings_db.update(update.key, update.value)

@router.delete("/{key}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def delete_setting(key: str) -> Dict[str, Any]:
    return settings_db.delete(key)