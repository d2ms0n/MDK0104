from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError, ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session
from database import DBUser, get_db
from models import UserRole

# Настройки для JWT токенов
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
	"""Сервис для работы с аутентификацией и авторизацией"""
	
	@staticmethod
	def verify_password(plain_password: str, hashed_password: str) -> bool:
		"""Проверка пароля"""
		try:
			return pwd_context.verify(plain_password, hashed_password)
		except ValueError as e:
			# Обработка ошибок, связанных с длиной пароля
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Password verification error: {str(e)}"
			)
	
	@staticmethod
	def get_password_hash(password: str) -> str:
		"""Хеширование пароля"""
		return pwd_context.hash(password)
	

	
	@staticmethod
	def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
		"""Создание JWT токена"""
		to_encode = data.copy()
		if expires_delta:
			expire = datetime.utcnow() + expires_delta
		else:
			expire = datetime.utcnow() + timedelta(minutes=65)
		to_encode.update({"exp": expire})
		encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
		return encoded_jwt
	
	@staticmethod
	def verify_token(token: str) -> Optional[dict]:
		"""Проверка JWT токена"""
		try:
			payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
			return payload
		except ExpiredSignatureError:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Token expired"
			)
		except InvalidTokenError:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid token"
			)
		except PyJWTError as e:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail=f"Could not validate credentials: {str(e)}"
			)

def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(security),
	db: Session = Depends(get_db)
) -> DBUser:
	"""Получение текущего пользователя из токена"""
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	
	try:
		# Проверяем токен
		payload = AuthService.verify_token(credentials.credentials)
		
		# Получаем username из токена
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception
		
		# Находим пользователя в базе данных
		user = db.query(DBUser).filter(DBUser.username == username).first()
		if user is None:
			raise credentials_exception
		
		return user
	except HTTPException:
		raise
	except Exception:
		raise credentials_exception

def require_role(required_roles: List[UserRole]):
	"""Декоратор для проверки ролей пользователя"""
	def role_checker(current_user: DBUser = Depends(get_current_user)):
		if current_user.role not in required_roles:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Not enough permissions"
			)
		return current_user
	return role_checker

def require_admin(current_user: DBUser = Depends(get_current_user)) -> DBUser:
	"""Требует роль администратора"""
	if current_user.role != UserRole.ADMIN:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Admin access required"
		)
	return current_user

def require_manager_or_admin(current_user: DBUser = Depends(get_current_user)) -> DBUser:
	"""Требует роль менеджера или администратора"""
	if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Manager or Admin access required"
		)
	return current_user

def require_any_role(current_user: DBUser = Depends(get_current_user)) -> DBUser:
	"""Требует любую валидную роль (авторизованный пользователь)"""
	return current_user
