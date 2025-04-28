from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ModType(str, Enum):
    GAMING = "gaming"
    NIGHT = "night"
    MEDIA = "media"
    CUSTOM = "custom"

class Priority(int, Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10

class ModBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="Name of the mod"
    )
    type: ModType
    description: Optional[str] = Field(
        None, 
        max_length=200
    )
    config: Dict[str, Any] = {}

    @validator('name')
    def name_must_be_valid(cls, v):
        # Ensure name doesn't contain special characters
        import re
        if not re.match(r'^[a-zA-Z0-9_\s-]+$', v):
            raise ValueError('Mod name can only contain letters, numbers, spaces, underscores, and hyphens')
        return v

class ModCreate(ModBase):
    priority: Priority = Priority.MEDIUM

class ModUpdate(BaseModel):
    name: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50
    )
    description: Optional[str] = Field(
        None, 
        max_length=200
    )
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[Priority] = None

class ModResponse(ModBase):
    id: int
    is_active: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ConditionBase(BaseModel):
    condition_type: str = Field(
        ..., 
        description="Type of condition (e.g., process, time, system state)"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Parameters for the condition"
    )
    logic_operator: str = Field(
        default="AND", 
        pattern="^(AND|OR)$", 
        description="Logical operator for combining conditions"
    )

    @validator('condition_type')
    def validate_condition_type(cls, v):
        valid_types = ['process', 'time', 'system_state', 'custom']
        if v.lower() not in valid_types:
            raise ValueError(f'Invalid condition type. Must be one of {valid_types}')
        return v

class ActionBase(BaseModel):
    action_type: str = Field(
        ..., 
        description="Type of action to perform"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Parameters for the action"
    )

    @validator('action_type')
    def validate_action_type(cls, v):
        valid_types = ['mod_activation', 'system_command', 'notification', 'custom']
        if v.lower() not in valid_types:
            raise ValueError(f'Invalid action type. Must be one of {valid_types}')
        return v

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