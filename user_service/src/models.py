from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
        favorites: Relationship to Favorite model.
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

    # Relationship к избранным фильмам
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Favorite(Base):
    """
    Модель избранных фильмов пользователя.

    Хранит информацию о фильмах, добавленных пользователем в избранное,
    включая закешированные данные из Movie Service для быстрого доступа.

    Attributes:
        id (int): Уникальный идентификатор записи (первичный ключ).
        user_id (int): ID пользователя (внешний ключ).
        movie_id (int): ID фильма в TMDB.
        movie_title (str): Название фильма (кэшировано).
        movie_poster_path (str | None): Путь к постеру (кэшировано).
        added_at (datetime): Дата и время добавления в избранное.
        user: Relationship to User model.
    """
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    movie_title: Mapped[str] = mapped_column(String(500), nullable=False)
    movie_poster_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationship к пользователю
    user: Mapped["User"] = relationship("User", back_populates="favorites")

    # Уникальное ограничение: один фильм может быть добавлен пользователем только один раз
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),
    )