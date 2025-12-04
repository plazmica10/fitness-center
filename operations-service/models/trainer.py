from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Trainer(BaseModel):
    trainer_id: Optional[UUID] = None
    name: str
    specialization: str
    rating: Optional[float] = None
