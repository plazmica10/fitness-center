from fastapi import APIRouter, HTTPException
from typing import List
from models.trainer import Trainer
from db import select_all, insert_one, select_one, update_one, delete_one
from utils.validators import (
    ValidationError,
    validate_trainer_rating
)

router = APIRouter(prefix="/trainers", tags=["trainers"])


@router.get("/", response_model=List[Trainer])
def list_trainers():
    rows = select_all("trainers")
    return rows


@router.post("/", response_model=Trainer)
def create_trainer(trainer: Trainer):
    try:
        # Validate rating
        validate_trainer_rating(trainer.rating)
        
        trainer_dict = trainer.dict()
        generated_id = insert_one("trainers", trainer_dict)
        if generated_id and not trainer.trainer_id:
            trainer.trainer_id = generated_id
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
def update_trainer(trainer_id: str, trainer: Trainer):
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
def delete_trainer(trainer_id: str):
    existing = select_one("trainers", "trainer_id", trainer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trainer not found")
    try:
        delete_one("trainers", "trainer_id", trainer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete mutation failed: {e}")
    return {"ok": True}
