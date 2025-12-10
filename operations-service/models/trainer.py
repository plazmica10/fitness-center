from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class Trainer(BaseModel):
    trainer_id: Optional[UUID] = None
    name: str
    email: Optional[EmailStr] = None  # Optional for backward compatibility with existing data
    specialization: str
    rating: Optional[float] = None
    experience_years: Optional[int] = None
