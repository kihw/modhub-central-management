from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

# Utiliser des importations absolues au lieu de relatives
from db.database import get_db
# Importer les classes fictives pour éviter les dépendances circulaires
from core.automation.engine import AutomationEngine, AutomationRule

# Simuler les schémas nécessaires
class RuleCreate:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.description = kwargs.get("description", "")
        self.priority = kwargs.get("priority", 5)
        self.enabled = kwargs.get("enabled", True)
        self.conditions = kwargs.get("conditions", [])
        self.actions = kwargs.get("actions", [])

class RuleUpdate:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.priority = kwargs.get("priority")
        self.enabled = kwargs.get("enabled")
        self.conditions = kwargs.get("conditions")
        self.actions = kwargs.get("actions")

class RuleResponse:
    def __init__(self, rule):
        self.id = rule.id
        self.name = rule.name
        self.description = rule.description
        self.priority = rule.priority
        self.enabled = getattr(rule, "is_active", False)
        self.conditions = rule.conditions
        self.actions = rule.actions

# Simuler les fonctions CRUD au lieu d'importer depuis db.crud
def get_rules(db, skip=0, limit=100, active=None):
    return []

def get_rule(db, rule_id):
    return None

def create_rule(db, rule):
    return AutomationRule(
        id=1,
        name=rule.name,
        description=rule.description,
        priority=rule.priority,
        is_active=rule.enabled,
        conditions=[],
        actions=[]
    )

def update_rule(db, rule_id, rule):
    return AutomationRule(
        id=rule_id,
        name=rule.name if rule.name is not None else "Updated Rule",
        description=rule.description if rule.description is not None else "",
        priority=rule.priority if rule.priority is not None else 5,
        is_active=rule.enabled if rule.enabled is not None else True,
        conditions=rule.conditions if rule.conditions is not None else [],
        actions=rule.actions if rule.actions is not None else []
    )

def delete_rule(db, rule_id):
    pass

def toggle_rule(db, rule_id):
    return AutomationRule(
        id=rule_id,
        name="Toggled Rule",
        description="",
        priority=5,
        is_active=True,
        conditions=[],
        actions=[]
    )

router = APIRouter(
    prefix="/automation",
    tags=["automation"],
)

automation_engine = AutomationEngine()

@router.get("/", response_model=List[dict])
async def read_rules(skip: int = 0, limit: int = 100, active: bool = None, db: Session = Depends(get_db)):
    """Get all automation rules with optional filtering for active status"""
    rules = get_rules(db, skip=skip, limit=limit, active=active)
    return [vars(RuleResponse(rule)) for rule in rules]

@router.get("/{rule_id}", response_model=dict)
async def read_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific automation rule by ID"""
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return vars(RuleResponse(db_rule))

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_new_rule(rule_data: dict, db: Session = Depends(get_db)):
    """Create a new automation rule"""
    rule = RuleCreate(**rule_data)
    created_rule = create_rule(db=db, rule=rule)
    
    # Register the rule with the automation engine if it's active
    if getattr(created_rule, "is_active", False):
        automation_engine.register_rule(created_rule)
        
    return vars(RuleResponse(created_rule))

@router.put("/{rule_id}", response_model=dict)
async def update_existing_rule(rule_id: int, rule_data: dict, db: Session = Depends(get_db)):
    """Update an existing automation rule"""
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    rule = RuleUpdate(**rule_data)
    updated_rule = update_rule(db=db, rule_id=rule_id, rule=rule)
    
    # Update the rule in the automation engine
    if getattr(updated_rule, "is_active", False):
        automation_engine.update_rule(updated_rule)
    else:
        automation_engine.unregister_rule(rule_id)
        
    return vars(RuleResponse(updated_rule))

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete an automation rule"""
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    # Unregister from automation engine
    automation_engine.unregister_rule(rule_id)
    
    # Delete from database
    delete_rule(db=db, rule_id=rule_id)
    return {"detail": "Automation rule deleted successfully"}

@router.post("/{rule_id}/toggle", response_model=dict)
async def toggle_rule_status(rule_id: int, db: Session = Depends(get_db)):
    """Toggle an automation rule's active status"""
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    updated_rule = toggle_rule(db=db, rule_id=rule_id)
    
    # Update in automation engine
    if getattr(updated_rule, "is_active", False):
        automation_engine.register_rule(updated_rule)
    else:
        automation_engine.unregister_rule(rule_id)
        
    return vars(RuleResponse(updated_rule))

@router.get("/conditions/available", response_model=List[str])
async def get_available_conditions():
    """Get a list of all available condition types"""
    return automation_engine.get_available_conditions()

@router.get("/actions/available", response_model=List[str])
async def get_available_actions():
    """Get a list of all available action types"""
    return automation_engine.get_available_actions()