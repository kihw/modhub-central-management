from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ModType(str, Enum):
    GAMING = "gaming"
    NIGHT = "night"
    MEDIA = "media"
    CUSTOM = "custom"

class ModBase(BaseModel):
    name: str
    type: ModType
    description: Optional[str] = None
    config: Dict[str, Any] = {}

class ModCreate(ModBase):
    pass

class ModUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ModResponse(ModBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ConditionBase(BaseModel):
    condition_type: str
    parameters: Dict[str, Any] = {}
    logic_operator: str = "AND"

class ActionBase(BaseModel):
    action_type: str
    parameters: Dict[str, Any] = {}

class RuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    priority: int = 5

class RuleCreate(RuleBase):
    conditions: List[ConditionBase]
    actions: List[ActionBase]
    enabled: bool = True

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    conditions: Optional[List[ConditionBase]] = None
    actions: Optional[List[ActionBase]] = None
    enabled: Optional[bool] = None

class RuleResponse(RuleBase):
    id: int
    conditions: List[ConditionBase]
    actions: List[ActionBase]
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class LogCreate(BaseModel):
    level: str
    message: str
    source: Optional[str] = None
    timestamp: Optional[datetime] = None

class LogResponse(LogCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class SettingsUpdate(BaseModel):
    general: Optional[Dict[str, Any]] = None
    automation: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    ui: Optional[Dict[str, Any]] = None