from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

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

class MinecraftServer(Base):
    __tablename__ = "minecraft_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    host = Column(String)
    port = Column(Integer, default=25565)
    version = Column(String)
    path = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    mods = relationship("Mod", back_populates="server")
    logs = relationship("Log", back_populates="server")
    automation_rules = relationship("AutomationRule", back_populates="server")

class Mod(Base):
    __tablename__ = "mods"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("minecraft_servers.id"))
    name = Column(String, index=True)
    version = Column(String)
    source_url = Column(String)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    install_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config = Column(JSON)
    
    server = relationship("MinecraftServer", back_populates="mods")

class AutomationRule(Base):
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("minecraft_servers.id"))
    name = Column(String, index=True)
    trigger_type = Column(String)  # schedule, event, condition
    trigger_value = Column(String)  # cron expression or event name
    action_type = Column(String)  # backup, restart, update, command
    action_value = Column(String)  # command to execute or other relevant data
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)
    
    server = relationship("MinecraftServer", back_populates="automation_rules")

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("minecraft_servers.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String)  # INFO, WARNING, ERROR, DEBUG
    category = Column(String)  # SERVER, MOD, SYSTEM, SECURITY
    message = Column(Text)
    details = Column(JSON, nullable=True)
    
    server = relationship("MinecraftServer", back_populates="logs")
    user = relationship("User", back_populates="logs")

class Backup(Base):
    __tablename__ = "backups"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("minecraft_servers.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    path = Column(String)
    size_mb = Column(Float)
    is_automatic = Column(Boolean, default=False)
    description = Column(Text, nullable=True)

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
