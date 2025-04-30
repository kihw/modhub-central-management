from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from db.database import get_db
from db.models import Mod
from db.schemas import ModResponse, ModCreate, ModUpdate, ModToggle
from db.crud import get_mods, get_mod, create_mod, update_mod, delete_mod, toggle_mod
from core.mods.mod_manager import ModManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mods", tags=["mods"])
mod_manager = ModManager()

@router.get("/", response_model=List[ModResponse])
async def read_mods(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[ModResponse]:
    return get_mods(db, skip=skip, limit=limit, active=active)

@router.get("/{mod_id}", response_model=ModResponse)
async def read_mod(
    mod_id: int,
    db: Session = Depends(get_db)
) -> ModResponse:
    if mod := get_mod(db, mod_id=mod_id):
        return mod
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mod not found")

@router.post("/", response_model=ModResponse, status_code=status.HTTP_201_CREATED)
async def create_new_mod(
    mod: ModCreate,
    db: Session = Depends(get_db)
) -> ModResponse:
    try:
        return create_mod(db=db, mod=mod)
    except Exception as e:
        logger.error(f"Error creating mod: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create mod"
        )

@router.put("/{mod_id}", response_model=ModResponse)
async def update_existing_mod(
    mod_id: int,
    mod: ModUpdate,
    db: Session = Depends(get_db)
) -> ModResponse:
    if not get_mod(db, mod_id=mod_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mod not found")
    try:
        return update_mod(db=db, mod_id=mod_id, mod=mod)
    except Exception as e:
        logger.error(f"Error updating mod {mod_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update mod"
        )

@router.delete("/{mod_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_mod(
    mod_id: int,
    db: Session = Depends(get_db)
) -> None:
    if mod := get_mod(db, mod_id=mod_id):
        try:
            if mod.is_active:
                mod_manager.deactivate_mod(mod.type)
            delete_mod(db=db, mod_id=mod_id)
        except Exception as e:
            logger.error(f"Error deleting mod {mod_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete mod"
            )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mod not found")

@router.post("/{mod_id}/toggle", response_model=ModResponse)
async def toggle_mod_status(
    mod_id: int,
    toggle_data: ModToggle,
    db: Session = Depends(get_db)
) -> ModResponse:
    if not (mod := get_mod(db, mod_id=mod_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mod not found")
    
    try:
        updated_mod = toggle_mod(db=db, mod_id=mod_id, is_active=toggle_data.enabled)
        if updated_mod.is_active:
            mod_manager.activate_mod(updated_mod.type, updated_mod.config)
        else:
            mod_manager.deactivate_mod(updated_mod.type)
        return updated_mod
    except Exception as e:
        logger.error(f"Error toggling mod {mod_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle mod"
        )

@router.post("/{mod_id}/apply", response_model=ModResponse)
async def apply_mod(
    mod_id: int,
    db: Session = Depends(get_db)
) -> ModResponse:
    if not (mod := get_mod(db, mod_id=mod_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mod not found")
    
    try:
        mod_manager.activate_mod(mod.type, mod.config)
        return mod
    except Exception as e:
        logger.error(f"Error applying mod {mod_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply mod"
        )
    
@router.get("/active/count", response_model=int)
async def get_active_mods_count(db: Session = Depends(get_db)) -> int:
    return len([mod for mod in get_mods(db, active=True)])


@router.get("/active/count", response_model=int)
async def get_active_mods_count(db: Session = Depends(get_db)) -> int:
    return len([mod for mod in get_mods(db, active=True)])
