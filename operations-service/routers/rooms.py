from fastapi import APIRouter, HTTPException
from typing import List
from models.room import Room
from db import select_all, insert_one, select_one, update_one, delete_one

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=List[Room])
def list_rooms():
    rows = select_all("rooms")
    return rows


@router.post("/", response_model=Room)
def create_room(room: Room):
    room_dict = room.dict()
    generated_id = insert_one("rooms", room_dict)
    # If ID was generated, update the response model
    if generated_id and not room.room_id:
        room.room_id = generated_id
    return room


@router.get("/{room_id}", response_model=Room)
def get_room(room_id: str):
    r = select_one("rooms", "room_id", room_id)
    if not r:
        raise HTTPException(status_code=404, detail="Room not found")
    return r


@router.put("/{room_id}", response_model=Room)
def update_room(room_id: str, room: Room):
    existing = select_one("rooms", "room_id", room_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    room_dict = room.dict()
    update_one("rooms", "room_id", room_id, room_dict)
    room.room_id = room_id
    return room


@router.delete("/{room_id}")
def delete_room(room_id: str):
    existing = select_one("rooms", "room_id", room_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    try:
        delete_one("rooms", "room_id", room_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete mutation failed: {e}")

    return {"ok": True}
