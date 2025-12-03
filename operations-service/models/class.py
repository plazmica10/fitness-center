from pydantic import BaseModel
from datetime import datetime

class Attendance(BaseModel):
    event_id: int
    class_id: int
    member_id: int
    timestamp: datetime
    status: str  # "entered" or "left"
