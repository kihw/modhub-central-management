from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
import logging
from db.database import get_db
from db.models import Mod
from db.schemas import ModResponse, ModCreate, ModUpdate, ModToggle
from db.crud import get_mods, get_mod, create_mod, update_mod, delete_mod, toggle_mod
from core.mods.mod_manager import ModManager, ModStatus

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

# In backend/api/mods.py - improve the toggle_mod_status method
@router.post("/{mod_id}/toggle", response_model=ModResponse)
async def toggle_mod_status(
    mod_id: int,
    toggle_data: ModToggle,
    db: Session = Depends(get_db)
) -> ModResponse:
    if not (mod := get_mod(db, mod_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mod not found")
    
    try:
        updated_mod = toggle_mod(db=db, mod_id=mod_id, is_active=toggle_data.enabled)
        
        # Add more comprehensive error handling
        if not updated_mod:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update mod status in database"
            )
            
        # Get the mod manager instance
        mod_manager_result = True
        try:
            if updated_mod.is_active:
                mod_manager_result = mod_manager.activate_mod(updated_mod.type, updated_mod.config)
            else:
                mod_manager_result = mod_manager.deactivate_mod(updated_mod.type)
        except Exception as e:
            logger.error(f"Mod manager error when toggling mod {mod_id}: {e}")
            mod_manager_result = False
            
        # If mod manager operation failed but database updated, let's be transparent
        if not mod_manager_result:
            return JSONResponse(
                status_code=status.HTTP_207_MULTI_STATUS,
                content={
                    "mod": jsonable_encoder(updated_mod),
                    "warning": "Database updated but mod manager operation failed"
                }
            )
            
        return updated_mod
    except Exception as e:
        logger.error(f"Error toggling mod {mod_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle mod: {str(e)}"
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
    
@router.get("/active/count")
async def get_active_mods_count(db: Session = Depends(get_db)) -> Dict[str, int]:
    try:
        active_mods = get_mods(db, active=True)
        return {"count": len(active_mods)}
    except Exception as e:
        # Ajoutez du logging pour comprendre l'erreur
        print(f"Error in get_active_mods_count: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Correctif Claude
@router.get("/active/count", response_model=Dict[str, int])
async def get_active_mods_count(db: Session = Depends(get_db)) -> Dict[str, int]:
    active_mods_count = len(get_mods(db, active=True))
    return {"count": active_mods_count}


# Correctif Claude
def activate_mod(self, mod_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
    with self._mod_lock:
        mod_state = self._mods.get(mod_id)
        if not mod_state or mod_state.status == ModStatus.ACTIVE:
            return False

        try:
            # Gestion des conflits de mods
            conflicts = self._check_conflicts(mod_state.instance)
            if conflicts:
                self._resolve_conflicts(mod_state.instance, conflicts)

            if config:
                mod_state.config.update(config)
                mod_state.instance.update_config(mod_state.config)

            if mod_state.instance.activate():
                mod_state.status = ModStatus.ACTIVE
                self._active_mods[mod_id] = mod_state.instance
                return True
                
            mod_state.status = ModStatus.ERROR
            return False
        except Exception as e:
            logger.error(f"Activation failed for mod {mod_id}: {str(e)}", exc_info=True)
            mod_state.status = ModStatus.ERROR
            return False
