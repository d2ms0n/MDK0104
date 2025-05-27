from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    price: float
    color: Optional[str] = None

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    color: Optional[str] = None

class Car(CarBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True