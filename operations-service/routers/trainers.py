from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from models.trainer import Trainer
from db import select_all, insert_one, select_one, update_one, delete_one
from utils.validators import (
    ValidationError,
    validate_trainer_rating
)
from auth_middleware import get_current_user, require_admin
from services.user_service_sync import create_user_for_trainer, delete_user_for_trainer

router = APIRouter(prefix="/trainers", tags=["trainers"])


@router.get("/", response_model=List[Trainer])
def list_trainers():
    rows = select_all("trainers")
    return rows


@router.post("/", response_model=Trainer)
async def create_trainer(trainer: Trainer, current_user: dict = Depends(require_admin)):
    try:
        # Validate rating
        if trainer.rating is not None:
            validate_trainer_rating(trainer.rating)
        
        # First create in ClickHouse (operations DB)
        trainer_dict = trainer.dict()
        generated_id = insert_one("trainers", trainer_dict)
        if generated_id and not trainer.trainer_id:
            trainer.trainer_id = generated_id
        
        # Then sync to user service (MongoDB)
        # This creates a user account for the trainer
        await create_user_for_trainer(
            trainer_id=str(trainer.trainer_id),
            name=trainer.name,
            email=trainer.email,
            password=None  # Will auto-generate
        )
        
        return trainer
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.get("/{trainer_id}", response_model=Trainer)
def get_trainer(trainer_id: str):
    t = select_one("trainers", "trainer_id", trainer_id)
    if not t:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return t


@router.put("/{trainer_id}", response_model=Trainer)
def update_trainer(trainer_id: str, trainer: Trainer, current_user: dict = Depends(require_admin)):
    existing = select_one("trainers", "trainer_id", trainer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    try:
        # Validate rating
        validate_trainer_rating(trainer.rating)
        
        trainer_dict = trainer.dict()
        update_one("trainers", "trainer_id", trainer_id, trainer_dict)
        trainer.trainer_id = trainer_id
        return trainer
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{trainer_id}")
async def delete_trainer(trainer_id: str, request: Request, current_user: dict = Depends(require_admin)):
    existing = select_one("trainers", "trainer_id", trainer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trainer not found")
    try:
        # Delete from ClickHouse
        delete_one("trainers", "trainer_id", trainer_id)
        
        # Also delete from user service (best effort) using trainer name to derive username
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        bearer = auth_header.split(" ", 1)[1] if auth_header and " " in auth_header else None
        await delete_user_for_trainer(trainer_id, name=existing.get("name"), bearer_token=bearer)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete mutation failed: {e}")
    return {"ok": True}
