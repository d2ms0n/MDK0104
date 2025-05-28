from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import Car
from repository import CarRepository, UserRepository
from schemas import CarCreate, CarUpdate
from database import get_db, DBUser
from sqlalchemy.orm import Session

from datetime import timedelta


from models import  User, UserCreate, UserUpdate, UserLogin, Token, UserChangePassword, UserRole
from repository import UserRepository
from auth import AuthService, get_current_user, require_admin, require_manager_or_admin, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_car_repository(db: Session = Depends(get_db)):
    """Получение репозитория автомобилей"""
    return CarRepository(db)

def get_user_repository(db: Session = Depends(get_db)):
    """Получение репозитория пользователей"""
    return UserRepository(db)

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    repo = CarRepository(db)

    if not repo.get_all():
        repo.create({"brand": "Toyota", "model": "Camry", "year": 2020, "price": 25000})
        repo.create({"brand": "Honda", "model": "Accord", "year": 2021, "price": 27000})

    # Создание администратора 
    user_repo = UserRepository(db)
    admin = user_repo.get_by_username("admin")
    if not admin:
        user_repo.create({
            "username": "admin",
            "email": "admin@carshop.com",
            "password": "admin123",
            "full_name": "Администратор",
            "role": UserRole.ADMIN
        })
        print("Создан администратор: admin / admin123")

# ========== ЭНДПОИНТЫ АВТОМОБИЛЕЙ  ==========

@app.get("/cars", response_model=list[Car])
def get_all_cars(repo: CarRepository = Depends(get_car_repository)):
    return repo.get_all()

@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int, repo: CarRepository = Depends(get_car_repository)):
    car = repo.get_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден"
        )
    return car

@app.post("/cars", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(car_data: CarCreate, repo: CarRepository = Depends(get_car_repository)):
    return repo.create(car_data.model_dump())

@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, car_data: CarUpdate, repo: CarRepository = Depends(get_car_repository)):
    car = repo.update(car_id, car_data.model_dump(exclude_unset=True))
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден"
        )
    return car

@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int, repo: CarRepository = Depends(get_car_repository)):
    if not repo.delete(car_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден"
        )
    return None

# ========== ЭНДПОИНТЫ АУТЕНТИФИКАЦИИ ==========

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin, user_repo: UserRepository = Depends(get_user_repository)):
    """Вход в систему"""
    user = user_repo.authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=User)
def get_current_user_info(current_user: DBUser = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return User(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active == "true",
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@app.post("/auth/change-password")
def change_password(
    password_data: UserChangePassword,
    current_user: DBUser = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Смена пароля текущего пользователя"""
    success = user_repo.change_password(
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Текущий пароль не корректный"
        )
    return {"message": "Пароль изменен"}

# ========== ЭНДПОИНТЫ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ ==========

@app.get("/users", response_model=list[User])
def get_all_users(
    current_user: DBUser = Depends(require_manager_or_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Получить всех пользователей (доступно менеджерам и администраторам)"""
    return user_repo.get_all()

@app.get("/users/{user_id}", response_model=User)
def get_user(
    user_id: int,
    current_user: DBUser = Depends(require_manager_or_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Получить пользователя по ID"""
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: DBUser = Depends(require_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Создать нового пользователя (только для администраторов)"""
    # Проверяем, что пользователь с таким именем не существует
    if user_repo.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем существует"
        )
    # Проверяем, что пользователь с таким email не существует
    if user_repo.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой email уже занят"
        )    
    return user_repo.create(user_data.model_dump())

@app.put("/users/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: DBUser = Depends(require_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Обновить пользователя (только для администраторов)"""
    user = user_repo.update(user_id, user_data.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: DBUser = Depends(require_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Удалить пользователя (только для администраторов)"""
    if not user_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return None




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)