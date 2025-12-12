from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class Attendance(BaseModel):
    event_id: Optional[UUID] = None
    class_id: UUID
    member_id: str  # MongoDB ObjectId string
    timestamp: datetime
    status: str  # "confirmed", "checked-in", "checked-out", or "cancelled"
