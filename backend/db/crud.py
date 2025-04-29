from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any, Union, Type
from datetime import datetime
import json
import logging

from .models import (
    Mod, AutomationRule, Condition, Action, Log,
    Process, Setting, DeviceState, Variable, ActionLog
)
from .schemas import ModCreate, ModUpdate, RuleCreate, RuleUpdate, LogCreate

logger = logging.getLogger(__name__)

# ======================== Mod CRUD Operations ========================

def get_mod(db: Session, mod_id: int) -> Optional[Mod]:
    """Get a mod by ID"""
    return db.query(Mod).filter(Mod.id == mod_id).first()

def get_mod_by_type(db: Session, mod_type: str) -> Optional[Mod]:
    """Get a mod by type (e.g., 'gaming', 'night', 'media')"""
    return db.query(Mod).filter(Mod.type == mod_type).first()

def get_mods(db: Session, skip: int = 0, limit: int = 100, active: Optional[bool] = None) -> List[Mod]:
    """Get all mods with optional filtering for active status"""
    query = db.query(Mod)
    
    if active is not None:
        query = query.filter(Mod.is_active == active)
        
    return query.offset(skip).limit(limit).all()

def create_mod(db: Session, mod: ModCreate) -> Mod:
    """Create a new mod"""
    db_mod = Mod(
        name=mod.name,
        type=mod.type.value,
        description=mod.description,
        is_active=False,
        priority=mod.priority.value,
        config=mod.config,
    )
    db.add(db_mod)
    db.commit()
    db.refresh(db_mod)
    return db_mod

def update_mod(db: Session, mod_id: int, mod: ModUpdate) -> Optional[Mod]:
    """Update an existing mod"""
    db_mod = get_mod(db, mod_id)
    if not db_mod:
        return None
    
    update_data = mod.dict(exclude_unset=True)
    
    # Handle special cases for enum values
    if 'priority' in update_data and update_data['priority'] is not None:
        update_data['priority'] = update_data['priority'].value
    
    for key, value in update_data.items():
        setattr(db_mod, key, value)
    
    db.commit()
    db.refresh(db_mod)
    return db_mod

def delete_mod(db: Session, mod_id: int) -> bool:
    """Delete a mod"""
    db_mod = get_mod(db, mod_id)
    if not db_mod:
        return False
        
    db.delete(db_mod)
    db.commit()
    return True

def toggle_mod(db: Session, mod_id: int, is_active: Optional[bool] = None) -> Optional[Mod]:
    """Toggle or set a mod's active status"""
    db_mod = get_mod(db, mod_id)
    if not db_mod:
        return None
        
    if is_active is None:
        db_mod.is_active = not db_mod.is_active
    else:
        db_mod.is_active = is_active
        
    db.commit()
    db.refresh(db_mod)
    return db_mod

# ======================== Rule CRUD Operations ========================

def get_rule(db: Session, rule_id: int) -> Optional[AutomationRule]:
    """Get a rule by ID"""
    return db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()

def get_rules(db: Session, skip: int = 0, limit: int = 100, active: Optional[bool] = None) -> List[AutomationRule]:
    """Get all rules with optional filtering"""
    query = db.query(AutomationRule)
    
    if active is not None:
        query = query.filter(AutomationRule.is_active == active)
        
    return query.offset(skip).limit(limit).all()

def create_rule(db: Session, rule: RuleCreate) -> AutomationRule:
    """Create a new automation rule with conditions and actions"""
    db_rule = AutomationRule(
        name=rule.name,
        description=rule.description,
        priority=rule.priority,
        is_active=rule.enabled
    )
    
    db.add(db_rule)
    db.flush()  # Get ID for relationships without committing
    
    # Add conditions
    for condition_data in rule.conditions:
        condition = Condition(
            rule_id=db_rule.id,
            condition_type=condition_data.condition_type,
            parameters=condition_data.parameters,
            logic_operator=condition_data.logic_operator
        )
        db.add(condition)
    
    # Add actions
    for action_data in rule.actions:
        action = Action(
            rule_id=db_rule.id,
            action_type=action_data.action_type,
            parameters=action_data.parameters
        )
        db.add(action)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

def update_rule(db: Session, rule_id: int, rule: RuleUpdate) -> Optional[AutomationRule]:
    """Update an existing automation rule"""
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        return None
    
    # Update rule base fields
    update_data = rule.dict(exclude={"conditions", "actions"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    
    # Update conditions if provided
    if rule.conditions is not None:
        # Delete existing conditions
        db.query(Condition).filter(Condition.rule_id == rule_id).delete()
        
        # Add new conditions
        for condition_data in rule.conditions:
            condition = Condition(
                rule_id=rule_id,
                condition_type=condition_data.condition_type,
                parameters=condition_data.parameters,
                logic_operator=condition_data.logic_operator
            )
            db.add(condition)
    
    # Update actions if provided
    if rule.actions is not None:
        # Delete existing actions
        db.query(Action).filter(Action.rule_id == rule_id).delete()
        
        # Add new actions
        for action_data in rule.actions:
            action = Action(
                rule_id=rule_id,
                action_type=action_data.action_type,
                parameters=action_data.parameters
            )
            db.add(action)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

def delete_rule(db: Session, rule_id: int) -> bool:
    """Delete an automation rule"""
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        return False
    
    # Related conditions and actions will be deleted due to CASCADE
    db.delete(db_rule)
    db.commit()
    return True

def toggle_rule(db: Session, rule_id: int, is_active: Optional[bool] = None) -> Optional[AutomationRule]:
    """Toggle or set a rule's active status"""
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        return None
    
    if is_active is None:
        db_rule.is_active = not db_rule.is_active
    else:
        db_rule.is_active = is_active
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

# ======================== Log Operations ========================

def create_log(db: Session, log: LogCreate) -> Log:
    """Create a new log entry"""
    db_log = Log(
        level=log.level.value if hasattr(log.level, 'value') else log.level,
        message=log.message,
        source=log.source,
        timestamp=log.timestamp or datetime.utcnow(),
        details=log.details
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    level: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Log]:
    """Get logs with filtering options"""
    query = db.query(Log)
    
    if level:
        query = query.filter(Log.level == level)
    
    if source:
        query = query.filter(Log.source == source)
    
    if start_date:
        query = query.filter(Log.timestamp >= start_date)
    
    if end_date:
        query = query.filter(Log.timestamp <= end_date)
    
    return query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()

def clear_logs(db: Session, older_than: Optional[datetime] = None) -> int:
    """Clear logs, optionally only those older than a given date"""
    query = db.query(Log)
    
    if older_than:
        query = query.filter(Log.timestamp < older_than)
    
    count = query.count()
    query.delete()
    db.commit()
    return count

# ======================== Process Operations ========================

def get_processes(db: Session, active_only: bool = True) -> List[Process]:
    """Get all tracked processes"""
    query = db.query(Process)
    
    if active_only:
        query = query.filter(Process.is_active == True)
    
    return query.all()

def update_process_status(
    db: Session, 
    process_name: str, 
    pid: int, 
    is_active: bool = True,
    memory_percent: Optional[float] = None,
    cpu_percent: Optional[float] = None
) -> Process:
    """Update or create a process status"""
    process = db.query(Process).filter(
        Process.name == process_name, 
        Process.pid == pid
    ).first()
    
    if not process:
        process = Process(
            name=process_name,
            pid=pid,
            is_active=is_active,
            memory_percent=memory_percent,
            cpu_percent=cpu_percent,
            last_seen=datetime.utcnow()
        )
        db.add(process)
    else:
        process.is_active = is_active
        process.memory_percent = memory_percent or process.memory_percent
        process.cpu_percent = cpu_percent or process.cpu_percent
        process.last_seen = datetime.utcnow()
    
    db.commit()
    db.refresh(process)
    return process

# ======================== Settings Operations ========================

def get_settings(db: Session, category: Optional[str] = None) -> List[Setting]:
    """Get all settings, optionally filtered by category"""
    query = db.query(Setting)
    
    if category:
        query = query.filter(Setting.category == category)
    
    return query.all()

def get_setting(db: Session, key: str) -> Optional[Setting]:
    """Get a specific setting by key"""
    return db.query(Setting).filter(Setting.key == key).first()

def get_setting_value(db: Session, key: str, default: Any = None) -> Any:
    """Get a setting value, parsing JSON if needed"""
    setting = get_setting(db, key)
    if not setting:
        return default
    
    # Try to parse as JSON for complex settings
    try:
        return json.loads(setting.value)
    except (json.JSONDecodeError, TypeError):
        return setting.value

def update_setting(db: Session, key: str, value: Union[str, Dict, List, bool, int, float], category: str = "general", description: Optional[str] = None) -> Setting:
    """Update or create a setting"""
    # Convert non-string values to JSON
    if not isinstance(value, str):
        value = json.dumps(value)
    
    setting = get_setting(db, key)
    
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = Setting(
            key=key,
            value=value,
            category=category,
            description=description
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting

def delete_setting(db: Session, key: str) -> bool:
    """Delete a setting"""
    setting = get_setting(db, key)
    if not setting:
        return False
    
    db.delete(setting)
    db.commit()
    return True

# ======================== Variable Operations ========================

def get_variable(db: Session, var_id: int) -> Optional[Variable]:
    """Get a variable by ID"""
    return db.query(Variable).filter(Variable.id == var_id).first()

def get_variable_by_name(db: Session, name: str) -> Optional[Variable]:
    """Get a variable by name"""
    return db.query(Variable).filter(Variable.name == name).first()

def get_variables(db: Session) -> List[Variable]:
    """Get all variables"""
    return db.query(Variable).all()

def set_variable(db: Session, name: str, value: Any, var_type: Optional[str] = None) -> Variable:
    """Set or update a variable"""
    variable = get_variable_by_name(db, name)
    
    # Determine type if not provided
    if var_type is None:
        if isinstance(value, bool):
            var_type = "boolean"
        elif isinstance(value, (int, float)):
            var_type = "number"
        elif isinstance(value, (dict, list)):
            var_type = "json"
            value = json.dumps(value)
        else:
            var_type = "string"
    
    # Convert to string for storage
    if var_type == "json" and not isinstance(value, str):
        value = json.dumps(value)
    elif not isinstance(value, str):
        value = str(value)
    
    if variable:
        variable.value = value
        variable.type = var_type
    else:
        variable = Variable(
            name=name,
            value=value,
            type=var_type
        )
        db.add(variable)
    
    db.commit()
    db.refresh(variable)
    return variable

def get_typed_variable_value(variable: Variable) -> Any:
    """Get a variable's value converted to its proper type"""
    if not variable:
        return None
    
    if variable.type == "boolean":
        return variable.value.lower() in ("true", "yes", "1", "t")
    elif variable.type == "number":
        try:
            if "." in variable.value:
                return float(variable.value)
            else:
                return int(variable.value)
        except ValueError:
            return 0
    elif variable.type == "json":
        try:
            return json.loads(variable.value)
        except json.JSONDecodeError:
            return {}
    else:  # string or other
        return variable.value

def delete_variable(db: Session, name: str) -> bool:
    """Delete a variable"""
    variable = get_variable_by_name(db, name)
    if not variable:
        return False
    
    db.delete(variable)
    db.commit()
    return True
