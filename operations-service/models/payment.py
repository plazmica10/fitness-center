from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class Payment(BaseModel):
    payment_id: Optional[UUID] = None
    member_id: str  # MongoDB ObjectId string
    class_id: UUID
    amount: float
    timestamp: datetime
