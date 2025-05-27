from sqlalchemy.orm import Session
from models import Car
from database import DBCar, get_db
from typing import List, Optional
from datetime import datetime

class CarRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Car]:
        db_cars = self.db.query(DBCar).all()
        return [self._convert_to_pydantic(car) for car in db_cars]

    def get_by_id(self, car_id: int) -> Optional[Car]:
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        return self._convert_to_pydantic(db_car) if db_car else None

    def create(self, car_data: dict) -> Car:
        db_car = DBCar(**car_data)
        self.db.add(db_car)
        self.db.commit()
        self.db.refresh(db_car)
        return self._convert_to_pydantic(db_car)

    def update(self, car_id: int, car_data: dict) -> Optional[Car]:
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        if not db_car:
            return None
            
        for key, value in car_data.items():
            setattr(db_car, key, value)
            
        self.db.commit()
        self.db.refresh(db_car)
        return self._convert_to_pydantic(db_car)

    def delete(self, car_id: int) -> bool:
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        if not db_car:
            return False
            
        self.db.delete(db_car)
        self.db.commit()
        return True

    def _convert_to_pydantic(self, db_car: DBCar) -> Car:
        return Car(
            id=db_car.id,
            brand=db_car.brand,
            model=db_car.model,
            year=db_car.year,
            price=db_car.price,
            color=db_car.color,
            created_at=db_car.created_at,
            updated_at=db_car.updated_at
        )