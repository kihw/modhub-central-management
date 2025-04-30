from pydantic import BaseModel, Field, validator, conint, confloat
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
    name: str = Field(..., min_length=3, max_length=50)
    type: ModType
    description: Optional[str] = Field(None, max_length=200)
    config: Dict[str, Any] = Field(default_factory=dict)

    @validator('name')
    def name_must_be_valid(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9_\s-]+$', v):
            raise ValueError('Mod name can only contain letters, numbers, spaces, underscores, and hyphens')
        return v.strip()

    @validator('config')
    def validate_config(cls, v):
        return v or {}

class ModCreate(ModBase):
    priority: Priority = Priority.MEDIUM
    is_active: bool = False

class ModUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[Priority] = None

class ModResponse(ModBase):
    id: conint(gt=0)
    is_active: bool = False
    priority: Priority
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ModToggle(BaseModel):
    enabled: bool

class ConditionBase(BaseModel):
    condition_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    logic_operator: str = "AND"

    @validator('condition_type')
    def validate_condition_type(cls, v):
        valid_types = {'process', 'time', 'system_state', 'custom'}
        if v.lower() not in valid_types:
            raise ValueError(f'Invalid condition type. Must be one of {valid_types}')
        return v.lower()

    @validator('logic_operator')
    def validate_logic_operator(cls, v):
        valid_operators = {'AND', 'OR', 'NOT'}
        if v.upper() not in valid_operators:
            raise ValueError(f'Invalid logic operator. Must be one of {valid_operators}')
        return v.upper()

class ActionBase(BaseModel):
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: Priority = Priority.MEDIUM

    @validator('action_type')
    def validate_action_type(cls, v):
        valid_types = {'mod_activation', 'mod_deactivation', 'system_command', 'notification', 'custom'}
        if v.lower() not in valid_types:
            raise ValueError(f'Invalid action type. Must be one of {valid_types}')
        return v.lower()

class RuleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    priority: conint(ge=1, le=10) = Field(default=5)

class RuleCreate(RuleBase):
    conditions: List[ConditionBase]
    actions: List[ActionBase]
    enabled: bool = True

class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    priority: Optional[conint(ge=1, le=10)] = None
    conditions: Optional[List[ConditionBase]] = None
    actions: Optional[List[ActionBase]] = None
    enabled: Optional[bool] = None

class RuleResponse(RuleBase):
    id: conint(gt=0)
    conditions: List[ConditionBase]
    actions: List[ActionBase]
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class Config:
    from_attributes = True

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCreate(BaseModel):
    level: LogLevel = LogLevel.INFO
    message: str = Field(..., min_length=1, max_length=1000)
    source: Optional[str] = Field(None, max_length=100)
    timestamp: Optional[datetime] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class LogResponse(LogCreate):
    id: conint(gt=0)
    timestamp: datetime

    class Config:
        orm_mode = True

class SettingsUpdate(BaseModel):
    general: Dict[str, Any] = Field(default_factory=dict)
    automation: Dict[str, Any] = Field(default_factory=dict)
    performance: Dict[str, Any] = Field(default_factory=dict)
    ui: Dict[str, Any] = Field(default_factory=dict)

    @validator('*')
    def validate_settings(cls, v):
        return v or {}

class SystemInfoResponse(BaseModel):
    cpu_count: conint(gt=0)
    total_memory: conint(ge=0)
    total_disk: conint(ge=0)
    version: str = Field("0.1.0", pattern=r'^\d+\.\d+\.\d+$')
    platform: str
    python_version: str

class ProcessResponse(BaseModel):
    pid: conint(gt=0)
    name: str
    memory_percent: confloat(ge=0, le=100)
    cpu_percent: confloat(ge=0, le=100)
    status: str
    created_at: datetime

class ResourceUsageResponse(BaseModel):
    cpu_percent: confloat(ge=0, le=100)
    memory_percent: confloat(ge=0, le=100)
    disk_percent: confloat(ge=0, le=100)
    timestamp: datetime