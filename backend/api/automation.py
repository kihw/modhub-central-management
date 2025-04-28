from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import AutomationRule as RuleModel
from db.schemas import RuleCreate, RuleUpdate, RuleResponse
from db.crud import get_rules, get_rule, create_rule, update_rule, delete_rule, toggle_rule
from core.automation.engine import AutomationEngine

router = APIRouter(
    prefix="/automation",
    tags=["automation"],
)

automation_engine = AutomationEngine()

@router.get("/", response_model=List[RuleResponse])
async def read_rules(skip: int = 0, limit: int = 100, active: bool = None, db: Session = Depends(get_db)):
    """Get all automation rules with optional filtering for active status"""
    return get_rules(db, skip=skip, limit=limit, active=active)

@router.get("/{rule_id}", response_model=RuleResponse)
async def read_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific automation rule by ID"""
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return db_rule

@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """Create a new automation rule"""
    created_rule = create_rule(db=db, rule=rule)
    
    # Register the rule with the automation engine if it's active
    if created_rule.is_active:
        automation_engine.register_rule(created_rule)
        
    return created_rule

@router.put("/{rule_id}", response_model=RuleResponse)
async def update_existing_rule(rule_id: int, rule: RuleUpdate, db: Session = Depends(get_db)):
    """Update an existing automation rule"""
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    updated_rule = update_rule(db=db, rule_id=rule_id, rule=rule)
    
    # Update the rule in the automation engine
    if updated_rule.is_active:
        automation_engine.update_rule(updated_rule)
    else:
        automation_engine.unregister_rule(rule_id)
        
    return updated_rule

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

@router.post("/{rule_id}/toggle", response_model=RuleResponse)
async def toggle_rule_status(rule_id: int, db: Session = Depends(get_db)):
    """Toggle an automation rule's active status"""
    db_rule = get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    updated_rule = toggle_rule(db=db, rule_id=rule_id)
    
    # Update in automation engine
    if updated_rule.is_active:
        automation_engine.register_rule(updated_rule)
    else:
        automation_engine.unregister_rule(rule_id)
        
    return updated_rule

@router.get("/conditions/available", response_model=List[str])
async def get_available_conditions():
    """Get a list of all available condition types"""
    return automation_engine.get_available_conditions()

@router.get("/actions/available", response_model=List[str])
async def get_available_actions():
    """Get a list of all available action types"""
    return automation_engine.get_available_actions()