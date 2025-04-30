from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import json
import logging

from .models import (
    Mod, AutomationRule, Condition, Action, Log,
    Process, Setting, DeviceState, Variable, ActionLog
)
from .schemas import ModCreate, ModUpdate, RuleCreate, RuleUpdate, LogCreate

logger = logging.getLogger(__name__)

def get_mod(db: Session, mod_id: int) -> Optional[Mod]:
    return db.query(Mod).filter(Mod.id == mod_id).first()

def get_mod_by_type(db: Session, mod_type: str) -> Optional[Mod]:
    return db.query(Mod).filter(Mod.type == mod_type).first()

def get_mods(db: Session, skip: int = 0, limit: int = 100, active: Optional[bool] = None) -> List[Mod]:
    query = db.query(Mod)
    if active is not None:
        query = query.filter(Mod.is_active == active)
    return query.offset(skip).limit(limit).all()

def create_mod(db: Session, mod: ModCreate) -> Mod:
    db_mod = Mod(
        name=mod.name,
        type=mod.type.value,
        description=mod.description,
        is_active=False,
        priority=mod.priority.value,
        config=mod.config
    )
    try:
        db.add(db_mod)
        db.commit()
        db.refresh(db_mod)
        return db_mod
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating mod: {e}")
        raise

def update_mod(db: Session, mod_id: int, mod: ModUpdate) -> Optional[Mod]:
    db_mod = get_mod(db, mod_id)
    if not db_mod:
        return None
    
    update_data = mod.dict(exclude_unset=True)
    if 'priority' in update_data and update_data['priority'] is not None:
        update_data['priority'] = update_data['priority'].value
    
    for key, value in update_data.items():
        setattr(db_mod, key, value)
    
    try:
        db.commit()
        db.refresh(db_mod)
        return db_mod
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating mod: {e}")
        raise

def delete_mod(db: Session, mod_id: int) -> bool:
    db_mod = get_mod(db, mod_id)
    if not db_mod:
        return False
    try:
        db.delete(db_mod)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting mod: {e}")
        raise

def toggle_mod(db: Session, mod_id: int, is_active: Optional[bool] = None) -> Optional[Mod]:
    db_mod = get_mod(db, mod_id)
    if not db_mod:
        return None
    try:
        db_mod.is_active = not db_mod.is_active if is_active is None else is_active
        db.commit()
        db.refresh(db_mod)
        return db_mod
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling mod: {e}")
        raise

def get_rule(db: Session, rule_id: int) -> Optional[AutomationRule]:
    return db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()

def get_rules(db: Session, skip: int = 0, limit: int = 100, active: Optional[bool] = None) -> List[AutomationRule]:
    query = db.query(AutomationRule)
    if active is not None:
        query = query.filter(AutomationRule.is_active == active)
    return query.offset(skip).limit(limit).all()

def create_rule(db: Session, rule: RuleCreate) -> AutomationRule:
    db_rule = AutomationRule(
        name=rule.name,
        description=rule.description,
        priority=rule.priority,
        is_active=rule.enabled
    )
    try:
        db.add(db_rule)
        db.flush()

        if rule.conditions:
            conditions = [
                Condition(
                    rule_id=db_rule.id,
                    condition_type=c.condition_type,
                    parameters=c.parameters,
                    logic_operator=c.logic_operator
                ) for c in rule.conditions
            ]
            db.bulk_save_objects(conditions)

        if rule.actions:
            actions = [
                Action(
                    rule_id=db_rule.id,
                    action_type=a.action_type,
                    parameters=a.parameters
                ) for a in rule.actions
            ]
            db.bulk_save_objects(actions)

        db.commit()
        db.refresh(db_rule)
        return db_rule
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating rule: {e}")
        raise

def update_rule(db: Session, rule_id: int, rule: RuleUpdate) -> Optional[AutomationRule]:
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        return None

    try:
        update_data = rule.dict(exclude={"conditions", "actions"}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_rule, key, value)

        if rule.conditions is not None:
            db.query(Condition).filter(Condition.rule_id == rule_id).delete()
            conditions = [
                Condition(
                    rule_id=rule_id,
                    condition_type=c.condition_type,
                    parameters=c.parameters,
                    logic_operator=c.logic_operator
                ) for c in rule.conditions
            ]
            db.bulk_save_objects(conditions)

        if rule.actions is not None:
            db.query(Action).filter(Action.rule_id == rule_id).delete()
            actions = [
                Action(
                    rule_id=rule_id,
                    action_type=a.action_type,
                    parameters=a.parameters
                ) for a in rule.actions
            ]
            db.bulk_save_objects(actions)

        db.commit()
        db.refresh(db_rule)
        return db_rule
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating rule: {e}")
        raise

def delete_rule(db: Session, rule_id: int) -> bool:
    try:
        result = db.query(AutomationRule).filter(AutomationRule.id == rule_id).delete()
        db.commit()
        return bool(result)
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting rule: {e}")
        raise

def toggle_rule(db: Session, rule_id: int, is_active: Optional[bool] = None) -> Optional[AutomationRule]:
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        return None
    try:
        db_rule.is_active = not db_rule.is_active if is_active is None else is_active
        db.commit()
        db.refresh(db_rule)
        return db_rule
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling rule: {e}")
        raise

def create_log(db: Session, log: LogCreate) -> Log:
    db_log = Log(
        level=log.level.value if hasattr(log.level, 'value') else log.level,
        message=log.message,
        source=log.source,
        timestamp=log.timestamp or datetime.utcnow(),
        details=log.details
    )
    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating log: {e}")
        raise

def get_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    level: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Log]:
    query = db.query(Log)
    filters = []
    if level:
        filters.append(Log.level == level)
    if source:
        filters.append(Log.source == source)
    if start_date:
        filters.append(Log.timestamp >= start_date)
    if end_date:
        filters.append(Log.timestamp <= end_date)
    if filters:
        query = query.filter(and_(*filters))
    return query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()

def clear_logs(db: Session, older_than: Optional[datetime] = None) -> int:
    try:
        query = db.query(Log)
        if older_than:
            query = query.filter(Log.timestamp < older_than)
        count = query.count()
        query.delete()
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing logs: {e}")
        raise

def get_processes(db: Session, active_only: bool = True) -> List[Process]:
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
    try:
        process = db.query(Process).filter(
            and_(Process.name == process_name, Process.pid == pid)
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
            if memory_percent is not None:
                process.memory_percent = memory_percent
            if cpu_percent is not None:
                process.cpu_percent = cpu_percent
            process.last_seen = datetime.utcnow()
        
        db.commit()
        db.refresh(process)
        return process
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating process status: {e}")
        raise

def get_settings(db: Session, category: Optional[str] = None) -> List[Setting]:
    query = db.query(Setting)
    if category:
        query = query.filter(Setting.category == category)
    return query.all()

def get_setting(db: Session, key: str) -> Optional[Setting]:
    return db.query(Setting).filter(Setting.key == key).first()

def get_setting_value(db: Session, key: str, default: Any = None) -> Any:
    setting = get_setting(db, key)
    if not setting:
        return default
    try:
        return json.loads(setting.value)
    except (json.JSONDecodeError, TypeError):
        return setting.value

def update_setting(
    db: Session,
    key: str,
    value: Union[str, Dict, List, bool, int, float],
    category: str = "general",
    description: Optional[str] = None
) -> Setting:
    try:
        str_value = json.dumps(value) if not isinstance(value, str) else value
        setting = get_setting(db, key)
        
        if setting:
            setting.value = str_value
            if description:
                setting.description = description
        else:
            setting = Setting(
                key=key,
                value=str_value,
                category=category,
                description=description
            )
            db.add(setting)
        
        db.commit()
        db.refresh(setting)
        return setting
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating setting: {e}")
        raise

def delete_setting(db: Session, key: str) -> bool:
    try:
        result = db.query(Setting).filter(Setting.key == key).delete()
        db.commit()
        return bool(result)
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting setting: {e}")
        raise

def get_variable(db: Session, var_id: int) -> Optional[Variable]:
    return db.query(Variable).filter(Variable.id == var_id).first()

def get_variable_by_name(db: Session, name: str) -> Optional[Variable]:
    return db.query(Variable).filter(Variable.name == name).first()

def get_variables(db: Session) -> List[Variable]:
    return db.query(Variable).all()

def set_variable(db: Session, name: str, value: Any, var_type: Optional[str] = None) -> Variable:
    try:
        if var_type is None:
            var_type = (
                "boolean" if isinstance(value, bool) else
                "number" if isinstance(value, (int, float)) else
                "json" if isinstance(value, (dict, list)) else
                "string"
            )

        str_value = (
            json.dumps(value) if var_type == "json" and not isinstance(value, str)
            else str(value) if not isinstance(value, str)
            else value
        )

        variable = get_variable_by_name(db, name)
        if variable:
            variable.value = str_value
            variable.type = var_type
        else:
            variable = Variable(name=name, value=str_value, type=var_type)
            db.add(variable)

        db.commit()
        db.refresh(variable)
        return variable
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting variable: {e}")
        raise

def get_typed_variable_value(variable: Variable) -> Any:
    if not variable:
        return None
    try:
        if variable.type == "boolean":
            return variable.value.lower() in ("true", "yes", "1", "t")
        elif variable.type == "number":
            return float(variable.value) if "." in variable.value else int(variable.value)
        elif variable.type == "json":
            return json.loads(variable.value)
        return variable.value
    except (ValueError, json.JSONDecodeError):
        logger.error(f"Error converting variable value: {variable.name}")
        return None

def delete_variable(db: Session, name: str) -> bool:
    try:
        result = db.query(Variable).filter(Variable.name == name).delete()
        db.commit()
        return bool(result)
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting variable: {e}")
        raise