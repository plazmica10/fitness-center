from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from models.classes import Class as ClassModel
from db import select_all, insert_one, select_one, update_one, delete_one
from utils.validators import (
    ValidationError,
    validate_class_times,
    validate_class_capacity,
    check_room_availability,
    check_trainer_availability,
    validate_foreign_keys
)

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("/", response_model=List[ClassModel])
def list_classes():
    rows = select_all("classes")
    return rows


@router.post("/", response_model=ClassModel)
def create_class(c: ClassModel):
    try:
        # Validate times
        validate_class_times(c.start_time, c.end_time)
        
        # Validate capacity
        validate_class_capacity(c.capacity)
        
        # Validate foreign keys
        if c.trainer_id:
            validate_foreign_keys(None, trainer_id=c.trainer_id)
        if c.room_id:
            validate_foreign_keys(None, room_id=c.room_id)
        
        # Check room availability
        if c.room_id:
            check_room_availability(None, c.room_id, c.start_time, c.end_time)
        
        # Check trainer availability
        if c.trainer_id:
            check_trainer_availability(None, c.trainer_id, c.start_time, c.end_time)
        
        class_dict = c.dict()
        generated_id = insert_one("classes", class_dict)
        if generated_id and not c.class_id:
            c.class_id = generated_id
        return c
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.get("/{class_id}", response_model=ClassModel)
def get_class(class_id: str):
    c = select_one("classes", "class_id", class_id)
    if not c:
        raise HTTPException(status_code=404, detail="Class not found")
    return c


@router.put("/{class_id}", response_model=ClassModel)
def update_class(class_id: str, c: ClassModel):
    existing = select_one("classes", "class_id", class_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Class not found")
    
    try:
        # Validate times
        validate_class_times(c.start_time, c.end_time)
        
        # Validate capacity
        validate_class_capacity(c.capacity)
        
        # Validate foreign keys
        if c.trainer_id:
            validate_foreign_keys(None, trainer_id=c.trainer_id)
        if c.room_id:
            validate_foreign_keys(None, room_id=c.room_id)
        
        # Check room availability (exclude current class)
        if c.room_id:
            check_room_availability(None, c.room_id, c.start_time, c.end_time, exclude_class_id=class_id)
        
        # Check trainer availability (exclude current class)
        if c.trainer_id:
            check_trainer_availability(None, c.trainer_id, c.start_time, c.end_time, exclude_class_id=class_id)
        
        class_dict = c.dict()
        update_one("classes", "class_id", class_id, class_dict)
        c.class_id = class_id
        return c
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{class_id}")
def delete_class(class_id: str):
    existing = select_one("classes", "class_id", class_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Class not found")
    try:
        delete_one("classes", "class_id", class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete mutation failed: {e}")
    return {"ok": True}
