from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Room(BaseModel):
    room_id: Optional[UUID] = None
    name: str
    capacity: int
    has_equipment: bool = False
