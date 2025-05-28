import enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CarBase(BaseModel):
    """Базовая модель автомобиля"""
    brand: str
    model: str
    year: int
    price: float
    color: Optional[str] = None

class CarCreate(CarBase):
    """Модель создания автомобиля"""
    pass

class CarUpdate(BaseModel):
    """Модель обновления автомобиля"""
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    color: Optional[str] = None

class Car(CarBase):
    """Модель автомобиля"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserRole(enum.Enum):
    """Роли пользователей в системе"""
    ADMIN = "admin"      # Полный доступ ко всем функциям
    MANAGER = "manager"  # Управление автомобилями и просмотр пользователей
    BUYER = "buyer"      # Только просмотр автомобилей



class UserBase(BaseModel):
    """Базовая модель пользователя"""
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.BUYER

class UserCreate(UserBase):
    """Модель для создания пользователя"""
    password: str

class UserUpdate(BaseModel):
    """Модель для обновления пользователя"""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserChangePassword(BaseModel):
    """Модель для смены пароля"""
    current_password: str
    new_password: str

class User(UserBase):
    """Модель пользователя для ответов API"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    """Модель для входа в систему"""
    username: str
    password: str

class Token(BaseModel):
    """Модель токена для ответа при входе"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Данные из токена"""
    username: Optional[str] = None