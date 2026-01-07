from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class User(Base):
    """
    Модель пользователя системы.

    Хранит информацию о зарегистрированных пользователях, включая учетные данные
    и статус активности.

    Attributes:
        id (int): Уникальный идентификатор пользователя (первичный ключ).
        email (str): Электронная почта пользователя (уникальное поле).
        hashed_password (str): Хэшированный пароль пользователя.
        is_active (bool): Флаг активности учетной записи.
        created_at (datetime): Дата и время создания записи о пользователе.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Автоматически устанавливает текущее время при создании записи
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )