from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from db.database import get_db
from core.automation.engine import AutomationEngine
from db.crud import get_rules, get_rule, create_rule, update_rule, delete_rule, toggle_rule
from db.schemas import RuleCreate, RuleUpdate, RuleResponse
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/automation", tags=["automation"])
automation_engine = AutomationEngine()

@router.get("/", response_model=List[RuleResponse])
async def read_rules(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[RuleResponse]:
    rules = get_rules(db, skip=skip, limit=limit, active=active)
    return [RuleResponse.from_orm(rule) for rule in rules]

@router.get("/{rule_id}", response_model=RuleResponse)
async def read_rule(rule_id: int, db: Session = Depends(get_db)) -> RuleResponse:
    if rule := get_rule(db, rule_id=rule_id):
        return RuleResponse.from_orm(rule)
    raise HTTPException(status_code=404, detail="Automation rule not found")

@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_rule(rule_data: RuleCreate, db: Session = Depends(get_db)) -> RuleResponse:
    try:
        created_rule = create_rule(db=db, rule=rule_data)
        if created_rule.is_active:
            automation_engine.register_rule(created_rule)
        return RuleResponse.from_orm(created_rule)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{rule_id}", response_model=RuleResponse)
async def update_existing_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    db: Session = Depends(get_db)
) -> RuleResponse:
    if not (db_rule := get_rule(db, rule_id=rule_id)):
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    try:
        updated_rule = update_rule(db=db, rule_id=rule_id, rule=rule_data)
        if updated_rule.is_active:
            automation_engine.update_rule(updated_rule)
        else:
            automation_engine.unregister_rule(rule_id)
        return RuleResponse.from_orm(updated_rule)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{rule_id}")
async def delete_existing_rule(rule_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    if not get_rule(db, rule_id=rule_id):
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    try:
        automation_engine.unregister_rule(rule_id)
        delete_rule(db=db, rule_id=rule_id)
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{rule_id}/toggle", response_model=RuleResponse)
async def toggle_rule_status(rule_id: int, db: Session = Depends(get_db)) -> RuleResponse:
    if not (db_rule := get_rule(db, rule_id=rule_id)):
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    try:
        updated_rule = toggle_rule(db=db, rule_id=rule_id)
        if updated_rule.is_active:
            automation_engine.register_rule(updated_rule)
        else:
            automation_engine.unregister_rule(rule_id)
        return RuleResponse.from_orm(updated_rule)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conditions/available", response_model=List[str])
async def get_available_conditions() -> List[str]:
    return automation_engine.get_available_conditions()

@router.get("/actions/available", response_model=List[str])
async def get_available_actions() -> List[str]:
    return automation_engine.get_available_actions()