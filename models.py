from pydantic import BaseModel
from typing import Optional

class Car(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    price: float
    color: Optional[str] = None