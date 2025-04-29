# backend/api/mods.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

# Fix imports
from db.database import get_db
from db.models import Mod
from db.schemas import ModResponse, ModCreate, ModUpdate, ModToggle
from db.crud import get_mods, get_mod, create_mod, update_mod, delete_mod, toggle_mod
from core.mods.mod_manager import ModManager

# Create a logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["mods"],
)

mod_manager = ModManager()

@router.get("/", response_model=List[ModResponse])
async def read_mods(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    """Get all mods with optional filtering for active status"""
    return get_mods(db, skip=skip, limit=limit, active=active)

@router.get("/{mod_id}", response_model=ModResponse)
async def read_mod(mod_id: int, db: Session = Depends(get_db)):
    """Get a specific mod by ID"""
    db_mod = get_mod(db, mod_id=mod_id)
    if db_mod is None:
        raise HTTPException(status_code=404, detail="Mod not found")
    return db_mod

@router.post("/", response_model=ModResponse, status_code=status.HTTP_201_CREATED)
async def create_new_mod(mod: ModCreate, db: Session = Depends(get_db)):
    """Create a new mod configuration"""
    return create_mod(db=db, mod=mod)

@router.put("/{mod_id}", response_model=ModResponse)
async def update_existing_mod(mod_id: int, mod: ModUpdate, db: Session = Depends(get_db)):
    """Update an existing mod configuration"""
    db_mod = get_mod(db, mod_id=mod_id)
    if db_mod is None:
        raise HTTPException(status_code=404, detail="Mod not found")
    
    return update_mod(db=db, mod_id=mod_id, mod=mod)

@router.delete("/{mod_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_mod(mod_id: int, db: Session = Depends(get_db)):
    """Delete a mod configuration"""
    db_mod = get_mod(db, mod_id=mod_id)
    if db_mod is None:
        raise HTTPException(status_code=404, detail="Mod not found")
    
    delete_mod(db=db, mod_id=mod_id)
    return {"detail": "Mod deleted successfully"}

@router.post("/{mod_id}/toggle", response_model=ModResponse)
async def toggle_mod_status(
    mod_id: int, 
    toggle_data: ModToggle, 
    db: Session = Depends(get_db)
):
    """Toggle a mod's active status"""
    db_mod = get_mod(db, mod_id=mod_id)
    if db_mod is None:
        raise HTTPException(status_code=404, detail="Mod not found")
    
    updated_mod = toggle_mod(db=db, mod_id=mod_id, is_active=toggle_data.enabled)
    
    # Apply changes to running system
    if updated_mod.is_active:
        try:
            mod_manager.activate_mod(updated_mod.type, updated_mod.config)
        except Exception as e:
            logger.error(f"Error activating mod: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to activate mod: {str(e)}"
            )
    else:
        try:
            mod_manager.deactivate_mod(updated_mod.type)
        except Exception as e:
            logger.error(f"Error deactivating mod: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to deactivate mod: {str(e)}"
            )
        
    return updated_mod

@router.post("/{mod_id}/apply", response_model=ModResponse)
async def apply_mod(mod_id: int, db: Session = Depends(get_db)):
    """Apply a mod's settings without changing its saved active status"""
    db_mod = get_mod(db, mod_id=mod_id)
    if db_mod is None:
        raise HTTPException(status_code=404, detail="Mod not found")
    
    # Apply the mod through the manager
    try:
        mod_manager.activate_mod(db_mod.type, db_mod.config)
        logger.info(f"Mod {mod_id} applied successfully")
    except Exception as e:
        logger.error(f"Error applying mod {mod_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply mod: {str(e)}"
        )
    
    return db_mod

@router.get("/active/count")
async def get_active_mods_count(db: Session = Depends(get_db)):
    """Get the count of active mods"""
    active_mods = get_mods(db, active=True)
    return {"active_count": len(active_mods)}
