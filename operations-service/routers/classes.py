from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from models.classes import Class as ClassModel
from db import select_all, insert_one, select_one, update_one, delete_one

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("/", response_model=List[ClassModel])
def list_classes():
    rows = select_all("classes")
    return rows


@router.post("/", response_model=ClassModel)
def create_class(c: ClassModel):
    class_dict = c.dict()
    generated_id = insert_one("classes", class_dict)
    if generated_id and not c.class_id:
        c.class_id = generated_id
    return c


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
    class_dict = c.dict()
    update_one("classes", "class_id", class_id, class_dict)
    c.class_id = class_id
    return c


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
