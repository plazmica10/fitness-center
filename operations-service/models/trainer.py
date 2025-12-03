from pydantic import BaseModel

class Trainer(BaseModel):
    trainer_id: int
    name: str
    specialization: str
    rating: float | None = None
