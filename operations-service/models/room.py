from pydantic import BaseModel

class Room(BaseModel):
    room_id: int
    name: str
    capacity: int
    has_equipment: bool = False
