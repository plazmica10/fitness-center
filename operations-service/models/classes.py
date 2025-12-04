from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class Class(BaseModel):
    class_id: Optional[UUID] = None
    name: str
    trainer_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    start_time: datetime
    end_time: datetime
    capacity: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
