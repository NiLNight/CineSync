from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt

from .config import settings

# Настройка хэширования паролей с использованием алгоритма bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие введенного пароля хэшированному паролю.

    Args:
        plain_password (str): Введенный пользователем пароль в открытом виде.
        hashed_password (str): Хэшированный пароль, хранящийся в базе данных.

    Returns:
        bool: True если пароль верный, False в противном случае.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Генерирует безопасный хэш пароля для хранения в базе данных.

    Args:
        password (str): Пароль в открытом виде.

    Returns:
        str: Хэшированный пароль.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создает JWT токен с данными пользователя.

    Args:
        data (dict): Данные для включения в токен (payload).
        expires_delta (timedelta | None): Время жизни токена.
            Если не указано, используется значение по умолчанию.

    Returns:
        str: Закодированный JWT токен.
    """
    to_encode = data.copy()

    # Определяем время истечения токена
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Добавляем время истечения (exp) в токен
    to_encode.update({"exp": expire})

    # Шифруем данные с использованием секретного ключа и алгоритма из настроек
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt