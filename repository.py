from sqlalchemy.orm import Session
from models import Car
from database import DBCar, DBUser
from typing import List, Optional
from sqlalchemy.orm import Session
from typing import List, Optional
from models import User, UserRole
from auth import AuthService

class CarRepository:
    """Репозиторий для работы с автомобилями"""
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Car]:
        """Получить все автомобили"""
        db_cars = self.db.query(DBCar).all()
        return [self._convert_to_pydantic(car) for car in db_cars]

    def get_by_id(self, car_id: int) -> Optional[Car]:
        """Получить автомобиль по его id"""
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        return self._convert_to_pydantic(db_car) if db_car else None

    def create(self, car_data: dict) -> Car:
        """Создать автомобиль"""
        db_car = DBCar(**car_data)
        self.db.add(db_car)
        self.db.commit()
        self.db.refresh(db_car)
        return self._convert_to_pydantic(db_car)

    def update(self, car_id: int, car_data: dict) -> Optional[Car]:
        """Обновить автомобиль"""
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        if not db_car:
            return None
            
        for key, value in car_data.items():
            setattr(db_car, key, value)
            
        self.db.commit()
        self.db.refresh(db_car)
        return self._convert_to_pydantic(db_car)

    def delete(self, car_id: int) -> bool:
        """Удалить автомобиль"""
        db_car = self.db.query(DBCar).filter(DBCar.id == car_id).first()
        if not db_car:
            return False
            
        self.db.delete(db_car)
        self.db.commit()
        return True

    def _convert_to_pydantic(self, db_car: DBCar) -> Car:
        """преобразование модели базы данных в Pydantic-модель"""
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
class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[User]:
        """Получить всех пользователей"""
        db_users = self.db.query(DBUser).all()
        return [self._convert_to_pydantic(user) for user in db_users]

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        db_user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        return self._convert_to_pydantic(db_user) if db_user else None

    def get_by_username(self, username: str) -> Optional[DBUser]:
        """Получить пользователя по имени (для аутентификации)"""
        return self.db.query(DBUser).filter(DBUser.username == username).first()

    def get_by_email(self, email: str) -> Optional[DBUser]:
        """Получить пользователя по email"""
        return self.db.query(DBUser).filter(DBUser.email == email).first()

    def create(self, user_data: dict) -> User:
        """Создать нового пользователя"""
        # Хешируем пароль
        if 'password' in user_data:
            hashed_password = AuthService.get_password_hash(user_data.pop('password'))
            user_data['hashed_password'] = hashed_password
        
        # Создаем пользователя
        db_user = DBUser(**user_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._convert_to_pydantic(db_user)

    def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Обновить пользователя"""
        db_user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        if not db_user:
            return None
        
        # Если обновляется пароль, хешируем его
        if 'password' in user_data:
            hashed_password = AuthService.get_password_hash(user_data.pop('password'))
            user_data['hashed_password'] = hashed_password
        
        # Обновляем поля
        for key, value in user_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return self._convert_to_pydantic(db_user)

    def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        db_user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True

    def authenticate_user(self, username: str, password: str) -> Optional[DBUser]:
        """Аутентификация пользователя"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Смена пароля пользователя"""
        db_user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        if not db_user:
            return False
        
        # Проверяем текущий пароль
        if not AuthService.verify_password(current_password, db_user.hashed_password):
            return False
        
        # Устанавливаем новый пароль
        db_user.hashed_password = AuthService.get_password_hash(new_password)
        self.db.commit()
        return True

    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Получить пользователей по роли"""
        db_users = self.db.query(DBUser).filter(DBUser.role == role).all()
        return [self._convert_to_pydantic(user) for user in db_users]

    def _convert_to_pydantic(self, db_user: DBUser) -> User:
        """Конвертация модели БД в Pydantic модель"""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            role=db_user.role,
            is_active=db_user.is_active == "true",  # Конвертация строки в bool
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )