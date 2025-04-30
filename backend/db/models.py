from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ModType(str, enum.Enum):
    GAMING = "gaming"
    NIGHT = "night"
    MEDIA = "media"
    CUSTOM = "custom"

class LogLevel(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, server_default="1", nullable=False)
    is_admin = Column(Boolean, server_default="0", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", onupdate=datetime.utcnow, nullable=False)
    
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")
    mods = relationship("Mod", back_populates="user", cascade="all, delete-orphan")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(20), server_default="light", nullable=False)
    notifications_enabled = Column(Boolean, server_default="1", nullable=False)
    auto_backup = Column(Boolean, server_default="1", nullable=False)
    preferences = Column(JSON, server_default="{}", nullable=False)
    
    user = relationship("User", back_populates="settings")

class Mod(Base):
    __tablename__ = "mods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    type = Column(Enum(ModType), nullable=False, server_default=ModType.CUSTOM.value)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, server_default="0", nullable=False)
    priority = Column(Integer, server_default="5", nullable=False)
    config = Column(JSON, server_default="{}", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="mods")
    rules = relationship("AutomationRule", back_populates="mod", cascade="all, delete-orphan")

class Condition(Base):
    __tablename__ = "conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False)
    condition_type = Column(String(50), nullable=False)
    parameters = Column(JSON, server_default="{}", nullable=False)
    logic_operator = Column(String(10), server_default="AND", nullable=False)
    execution_order = Column(Integer, server_default="0", nullable=False)
    
    rule = relationship("AutomationRule", back_populates="conditions")

class Action(Base):
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False)
    parameters = Column(JSON, server_default="{}", nullable=False)
    execution_order = Column(Integer, server_default="0", nullable=False)
    timeout = Column(Integer, server_default="30", nullable=False)
    
    rule = relationship("AutomationRule", back_populates="actions")

class AutomationRule(Base):
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    mod_id = Column(Integer, ForeignKey("mods.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    priority = Column(Integer, server_default="5", nullable=False)
    is_active = Column(Boolean, server_default="1", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", onupdate=datetime.utcnow, nullable=False)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    cooldown = Column(Integer, server_default="0", nullable=False)
    
    mod = relationship("Mod", back_populates="rules")
    conditions = relationship("Condition", back_populates="rule", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="rule", cascade="all, delete-orphan")
    logs = relationship("ActionLog", back_populates="rule", cascade="all, delete-orphan")

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)
    level = Column(Enum(LogLevel), nullable=False)
    source = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, server_default="{}", nullable=True)
    
    user = relationship("User", back_populates="logs")

class Process(Base):
    __tablename__ = "processes"
    
    id = Column(Integer, primary_key=True, index=True)
    pid = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    path = Column(String(512), nullable=True)
    is_active = Column(Boolean, server_default="1", nullable=False)
    memory_percent = Column(Float, nullable=True)
    cpu_percent = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)
    last_seen = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)

class DeviceState(Base):
    __tablename__ = "device_states"
    
    id = Column(Integer, primary_key=True, index=True)
    device_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    state = Column(JSON, nullable=False)
    device_metadata = Column(JSON, server_default="{}", nullable=False) 
    timestamp = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)

class Variable(Base):
    __tablename__ = "variables"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    type = Column(String(20), server_default="string", nullable=False)
    scope = Column(String(50), server_default="global", nullable=False)
    is_system = Column(Boolean, server_default="0", nullable=False)

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    type = Column(String(20), server_default="string", nullable=False)
    category = Column(String(50), server_default="general", nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, server_default="0", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", onupdate=datetime.utcnow, nullable=False)

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP", nullable=False)
    action_type = Column(String(50), nullable=False)
    parameters = Column(JSON, server_default="{}", nullable=False)
    success = Column(Boolean, server_default="1", nullable=False)
    error_message = Column(Text, nullable=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(100), nullable=True)
    execution_time = Column(Float, nullable=True)
    
    rule = relationship("AutomationRule", back_populates="logs")