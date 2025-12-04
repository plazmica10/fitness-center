from fastapi import APIRouter, HTTPException
from typing import List
from models.attendance import Attendance
from db import select_all, insert_one, select_one, delete_one

router = APIRouter(prefix="/attendances", tags=["attendances"])


@router.get("/", response_model=List[Attendance])
def list_attendances():
    rows = select_all("attendances")
    return rows


# TODO: should call member service to verify member_id exists
@router.post("/", response_model=Attendance)
def create_attendance(att: Attendance):
    att_dict = att.dict()
    generated_id = insert_one("attendances", att_dict)
    if generated_id and not att.event_id:
        att.event_id = generated_id
    return att


@router.get("/{event_id}", response_model=Attendance)
def get_attendance(event_id: str):
    a = select_one("attendances", "event_id", event_id)
    if not a:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return a


@router.delete("/{event_id}")
def delete_attendance(event_id: str):
    existing = select_one("attendances", "event_id", event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Attendance not found")
    try:
        delete_one("attendances", "event_id", event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete mutation failed: {e}")
    return {"ok": True}
