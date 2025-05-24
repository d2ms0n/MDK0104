from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import Car
from repository import CarRepository
from schemas import CarCreate, CarUpdate

app = FastAPI()
repo = CarRepository()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

repo.create({"brand": "Toyota", "model": "Camry", "year": 2020, "price": 25000})
repo.create({"brand": "Honda", "model": "Accord", "year": 2021, "price": 27000})

@app.get("/cars", response_model=list[Car])
def get_all_cars():
    return repo.get_all()

@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int):
    car = repo.get_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    return car

@app.post("/cars", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(car_data: CarCreate):
    return repo.create(car_data.model_dump())

@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, car_data: CarUpdate):
    car = repo.update(car_id, car_data.model_dump(exclude_unset=True))
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    return car

@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int):
    if not repo.delete(car_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    return None

uvicorn.run(app)