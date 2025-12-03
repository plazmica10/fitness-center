from pydantic import BaseModel
from datetime import datetime

class Payment(BaseModel):
    payment_id: int
    member_id: int
    class_id: int
    amount: float
    timestamp: datetime
