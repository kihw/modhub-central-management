from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ModType(enum.Enum):
    GAMING = "gaming"
    NIGHT = "night"
    MEDIA = "media"
    CUSTOM = "custom"

class LogLevel(enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    logs = relationship("Log", back_populates="user")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme = Column(String, default="light")
    notifications_enabled = Column(Boolean, default=True)
    auto_backup = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="settings")

class Mod(Base):
    __tablename__ = "mods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, default="custom")  # gaming, night, media, custom
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    priority = Column(Integer, default=5)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rules = relationship("AutomationRule", back_populates="mod")

class Condition(Base):
    __tablename__ = "conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id"), nullable=False)
    condition_type = Column(String, nullable=False)
    parameters = Column(JSON, default={})
    logic_operator = Column(String, default="AND")
    
    rule = relationship("AutomationRule", back_populates="conditions")

class Action(Base):
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id"), nullable=False)
    action_type = Column(String, nullable=False)
    parameters = Column(JSON, default={})
    
    rule = relationship("AutomationRule", back_populates="actions")

class AutomationRule(Base):
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    mod_id = Column(Integer, ForeignKey("mods.id"), nullable=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)
    
    mod = relationship("Mod", back_populates="rules")
    conditions = relationship("Condition", back_populates="rule", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="rule", cascade="all, delete-orphan")

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String)  # INFO, WARNING, ERROR, DEBUG
    source = Column(String, nullable=True)  # mod, system, automation
    message = Column(Text)
    details = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="logs")

class Process(Base):
    __tablename__ = "processes"
    
    id = Column(Integer, primary_key=True, index=True)
    pid = Column(Integer)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    memory_percent = Column(Float, nullable=True)
    cpu_percent = Column(Float, nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
class DeviceState(Base):
    __tablename__ = "device_states"
    
    id = Column(Integer, primary_key=True, index=True)
    device_type = Column(String, index=True)  # keyboard, mouse, display, audio
    name = Column(String)
    state = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Variable(Base):
    __tablename__ = "variables"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    value = Column(String)
    type = Column(String, default="string")  # string, number, boolean, json

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
    category = Column(String, default="general")  # general, automation, ui, system
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_type = Column(String)
    parameters = Column(JSON, nullable=True)
    success = Column(Boolean, default=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id"), nullable=True)
    device_id = Column(String, nullable=True)
    
    rule = relationship("AutomationRule")
