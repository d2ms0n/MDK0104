from typing import Optional
from pydantic import BaseModel

class CarCreate(BaseModel):
    brand: str
    model: str
    year: int
    price: float
    color: Optional[str] = None

class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    color: Optional[str] = None

