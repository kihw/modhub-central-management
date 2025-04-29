from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from db.database import get_db
from core.automation.engine import AutomationEngine
from db.models import AutomationRule
from db.schemas import RuleCreate, RuleUpdate, RuleResponse

router = APIRouter(
    prefix="/automation",
    tags=["automation"],
)

automation_engine = AutomationEngine()

@router.get("/", response_model=List[Dict[str, Any]])
async def read_rules(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    """Get all automation rules with optional filtering for active status"""
    from db.crud import get_rules
    rules = get_rules(db, skip=skip, limit=limit, active=active)
    return [vars(RuleResponse(rule)) for rule in rules]

@router.get("/{rule_id}", response_model=Dict[str, Any])
async def read_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific automation rule by ID"""
    from db.crud import get_rule
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return vars(RuleResponse(db_rule))

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_new_rule(rule_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new automation rule"""
    from db.crud import create_rule
    rule = RuleCreate(**rule_data)
    created_rule = create_rule(db=db, rule=rule)
    
    # Register the rule with the automation engine if it's active
    if getattr(created_rule, "is_active", False):
        automation_engine.register_rule(created_rule)
        
    return vars(RuleResponse(created_rule))

@router.put("/{rule_id}", response_model=Dict[str, Any])
async def update_existing_rule(rule_id: int, rule_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Update an existing automation rule"""
    from db.crud import get_rule, update_rule
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
    from db.crud import get_rule, delete_rule
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    # Unregister from automation engine
    automation_engine.unregister_rule(rule_id)
    
    # Delete from database
    delete_rule(db=db, rule_id=rule_id)
    return {"detail": "Automation rule deleted successfully"}

@router.post("/{rule_id}/toggle", response_model=Dict[str, Any])
async def toggle_rule_status(rule_id: int, db: Session = Depends(get_db)):
    """Toggle an automation rule's active status"""
    from db.crud import get_rule, toggle_rule
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