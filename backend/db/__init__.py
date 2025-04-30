from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Mod(Base):
    __tablename__ = 'mods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    type = Column(String(50), nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False, index=True)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    rules = relationship("Rule", back_populates="mod", cascade="all, delete-orphan", lazy="select")
    events = relationship("EventLog", back_populates="mod", lazy="select")

    __table_args__ = (Index('idx_mod_type_priority', 'type', 'priority'),)

class Rule(Base):
    __tablename__ = 'rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mod_id = Column(Integer, ForeignKey('mods.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    mod = relationship("Mod", back_populates="rules", lazy="joined")

    __table_args__ = (
        Index('idx_mod_priority', 'mod_id', 'priority'),
        Index('idx_rule_enabled_priority', 'enabled', 'priority')
    )

class ProcessMapping(Base):
    __tablename__ = 'process_mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    process_name = Column(String(200), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    custom_settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (Index('idx_process_category', 'process_name', 'category'),)

class SystemState(Base):
    __tablename__ = 'system_states'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    active_processes = Column(JSON)
    active_mods = Column(JSON)
    system_metrics = Column(JSON)
    user_activity = Column(JSON)

    __table_args__ = (Index('idx_system_state_timestamp', 'timestamp', unique=True),)

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, unique=True, index=True)
    settings = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class EventLog(Base):
    __tablename__ = 'event_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    mod_id = Column(Integer, ForeignKey('mods.id', ondelete='SET NULL'), nullable=True)
    details = Column(JSON)
    severity = Column(String(20), default='info', nullable=False, index=True)
    
    mod = relationship("Mod", back_populates="events", lazy="select")

    __table_args__ = (
        Index('idx_timestamp_type', 'timestamp', 'event_type'),
        Index('idx_event_severity', 'severity', 'timestamp')
    )