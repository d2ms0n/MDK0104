from typing import List, Optional
from models import Car

class CarRepository:
    def __init__(self):
        self._cars: List[Car] = []
        self._next_id = 1

    def get_all(self) -> List[Car]:
        return self._cars.copy()

    def get_by_id(self, car_id: int) -> Optional[Car]:
        for car in self._cars:
            if car.id == car_id:
                return car
        return None

    def create(self, car_data: dict) -> Car:
        car = Car(id=self._next_id, **car_data)
        self._cars.append(car)
        self._next_id += 1
        return car

    def update(self, car_id: int, car_data: dict) -> Optional[Car]:
        for i, car in enumerate(self._cars):
            if car.id == car_id:
                updated_car = car.copy(update=car_data)
                self._cars[i] = updated_car
                return updated_car
        return None

    def delete(self, car_id: int) -> bool:
        for i, car in enumerate(self._cars):
            if car.id == car_id:
                self._cars.pop(i)
                return True
        return False