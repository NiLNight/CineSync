from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    """
    Базовая схема пользователя.

    Содержит общие поля, которые используются в других схемах.

    Attributes:
        email (EmailStr): Электронная почта пользователя с валидацией формата.
    """
    email: EmailStr


class UserCreate(UserBase):
    """
    Схема для регистрации нового пользователя.

    Расширяет базовую схему полем пароля, который передает клиент при регистрации.

    Attributes:
        password (str): Пароль пользователя для регистрации.
    """
    password: str


class UserResponse(UserBase):
    """
    Схема для ответа с информацией о пользователе.

    Используется для безопасного возврата данных пользователя без пароля.

    Attributes:
        id (int): Уникальный идентификатор пользователя.
        is_active (bool): Статус активности учетной записи.
        created_at (datetime): Дата и время создания учетной записи.
    """
    id: int
    is_active: bool
    created_at: datetime

    # Настройка для работы с ORM объектами SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """
    Схема для JWT токена.

    Используется для возврата аутентификационного токена.

    Attributes:
        access_token (str): JWT токен доступа.
        token_type (str): Тип токена (обычно "bearer").
    """
    access_token: str
    token_type: str