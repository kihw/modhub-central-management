from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from db. import models, schemas


def get_mod(db: Session, mod_id: int) -> Optional[models.Mod]:
    """Get a mod by ID"""
    return db.query(models.Mod).filter(models.Mod.id == mod_id).first()


def get_mods(db: Session, skip: int = 0, limit: int = 100) -> List[models.Mod]:
    """Get all mods with pagination"""
    return db.query(models.Mod).offset(skip).limit(limit).all()


def create_mod(db: Session, mod: schemas.ModCreate) -> models.Mod:
    """Create a new mod"""
    db_mod = models.Mod(
        name=mod.name,
        version=mod.version,
        author=mod.author,
        description=mod.description,
        path=mod.path,
        enabled=mod.enabled,
        installed_date=datetime.now()
    )
    db.add(db_mod)
    db.commit()
    db.refresh(db_mod)
    return db_mod


def update_mod(db: Session, mod_id: int, mod_data: schemas.ModUpdate) -> Optional[models.Mod]:
    """Update a mod"""
    db_mod = db.query(models.Mod).filter(models.Mod.id == mod_id).first()
    if not db_mod:
        return None
    
    update_data = mod_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mod, key, value)
    
    db.commit()
    db.refresh(db_mod)
    return db_mod


def delete_mod(db: Session, mod_id: int) -> bool:
    """Delete a mod"""
    db_mod = db.query(models.Mod).filter(models.Mod.id == mod_id).first()
    if not db_mod:
        return False
    
    db.delete(db_mod)
    db.commit()
    return True


def get_rule(db: Session, rule_id: int) -> Optional[models.Rule]:
    """Get a rule by ID"""
    return db.query(models.Rule).filter(models.Rule.id == rule_id).first()


def get_rules(db: Session, skip: int = 0, limit: int = 100) -> List[models.Rule]:
    """Get all rules with pagination"""
    return db.query(models.Rule).offset(skip).limit(limit).all()


def create_rule(db: Session, rule: schemas.RuleCreate) -> models.Rule:
    """Create a new rule"""
    db_rule = models.Rule(
        name=rule.name,
        condition=rule.condition,
        action=rule.action,
        enabled=rule.enabled,
        created_date=datetime.now()
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


def update_rule(db: Session, rule_id: int, rule_data: schemas.RuleUpdate) -> Optional[models.Rule]:
    """Update a rule"""
    db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not db_rule:
        return None
    
    update_data = rule_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


def delete_rule(db: Session, rule_id: int) -> bool:
    """Delete a rule"""
    db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not db_rule:
        return False
    
    db.delete(db_rule)
    db.commit()
    return True


def get_logs(db: Session, skip: int = 0, limit: int = 100, filter_params: Dict[str, Any] = None) -> List[models.Log]:
    """Get logs with pagination and optional filtering"""
    query = db.query(models.Log)
    
    if filter_params:
        if "level" in filter_params:
            query = query.filter(models.Log.level == filter_params["level"])
        if "start_date" in filter_params:
            query = query.filter(models.Log.timestamp >= filter_params["start_date"])
        if "end_date" in filter_params:
            query = query.filter(models.Log.timestamp <= filter_params["end_date"])
        if "source" in filter_params:
            query = query.filter(models.Log.source.like(f"%{filter_params['source']}%"))
    
    return query.order_by(models.Log.timestamp.desc()).offset(skip).limit(limit).all()


def create_log(db: Session, log: schemas.LogCreate) -> models.Log:
    """Create a new log entry"""
    db_log = models.Log(
        level=log.level,
        message=log.message,
        source=log.source,
        timestamp=datetime.now() if log.timestamp is None else log.timestamp
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_settings(db: Session) -> Dict[str, Any]:
    """Get all settings as a dictionary"""
    settings = db.query(models.Setting).all()
    return {setting.key: setting.value for setting in settings}


def get_setting(db: Session, key: str) -> Optional[models.Setting]:
    """Get a setting by key"""
    return db.query(models.Setting).filter(models.Setting.key == key).first()


def update_setting(db: Session, key: str, value: str) -> models.Setting:
    """Update or create a setting"""
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    
    if setting:
        setting.value = value
    else:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting