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


class TokenData(BaseModel):
    """
    Схема для данных, извлеченных из JWT токена.

    Attributes:
        sub (str): Email пользователя (subject claim).
        user_id (int): ID пользователя.
    """
    sub: str
    user_id: int


class FavoriteCreate(BaseModel):
    """
    Схема для добавления фильма в избранное.

    Attributes:
        movie_id (int): Уникальный идентификатор фильма в TMDB.
    """
    movie_id: int


class FavoriteResponse(BaseModel):
    """
    Схема для ответа с информацией об избранном фильме.

    Attributes:
        id (int): ID записи в базе данных.
        user_id (int): ID пользователя.
        movie_id (int): ID фильма в TMDB.
        movie_title (str): Название фильма.
        movie_poster_path (str | None): Путь к постеру.
        added_at (datetime): Дата добавления.
    """
    id: int
    user_id: int
    movie_id: int
    movie_title: str
    movie_poster_path: str | None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)