from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import httpx

from .models import User, Favorite
from .schemas import UserCreate
from .security import get_password_hash, verify_password
from .config import settings


class UserService:
    """
    Сервис для управления пользователями.

    Реализует бизнес-логику работы с пользователями: регистрацию, аутентификацию.
    Работает с базой данных через асинхронную сессию SQLAlchemy.

    Attributes:
        db (AsyncSession): Сессия базы данных для выполнения запросов.
        http_client (httpx.AsyncClient | None): HTTP клиент для межсервисных запросов.
    """

    def __init__(self, db: AsyncSession, http_client: httpx.AsyncClient | None = None):
        self.db = db
        self.http_client = http_client

    async def create_user(self, user_in: UserCreate) -> User:
        """
        Регистрирует нового пользователя в системе.

        Args:
            user_in (UserCreate): Данные для регистрации (email и пароль).

        Returns:
            User: Созданный пользователь (ORM-объект).

        Raises:
            HTTPException: Если пользователь с таким email уже существует.
        """
        # Проверяем, занят ли email
        query = select(User).where(User.email == user_in.email)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Создаем пользователя с хэшированным паролем
        new_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            is_active=True
        )

        # Сохраняем пользователя в базе данных
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Аутентифицирует пользователя по email и паролю.

        Args:
            email (str): Email пользователя для входа.
            password (str): Пароль пользователя для входа.

        Returns:
            User | None: Объект пользователя при успешной аутентификации,
            None в случае неудачи.
        """
        # Ищем пользователя по email
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        # Проверяем, существует ли пользователь и совпадает ли пароль
        if not user or not verify_password(password, user.hashed_password):
            return None

        return user

    async def add_to_favorites(self, user_id: int, movie_id: int) -> Favorite:
        """
        Добавляет фильм в избранное пользователя.

        Сначала проверяет существование фильма через запрос к Movie Service,
        затем создает запись в БД с закешированными данными о фильме.

        Args:
            user_id (int): ID пользователя.
            movie_id (int): ID фильма в TMDB.

        Returns:
            Favorite: Созданная запись об избранном фильме.

        Raises:
            HTTPException: 404 если фильм не найден, 400 если уже в избранном.
        """
        if not self.http_client:
            raise HTTPException(
                status_code=500,
                detail="HTTP client not configured"
            )

        # Запрос к Movie Service для получения деталей фильма
        try:
            response = await self.http_client.get(
                f"{settings.MOVIE_SERVICE_URL}/movies/{movie_id}"
            )
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Movie with ID {movie_id} not found"
                )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to communicate with Movie Service: {str(e)}"
            )

        movie_data = response.json()

        # Создаем запись в избранном с закешированными данными
        favorite = Favorite(
            user_id=user_id,
            movie_id=movie_id,
            movie_title=movie_data.get("title", "Unknown"),
            movie_poster_path=movie_data.get("poster_path")
        )

        try:
            self.db.add(favorite)
            await self.db.commit()
            await self.db.refresh(favorite)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Movie already in favorites"
            )

        return favorite

    async def get_user_favorites(self, user_id: int) -> list[Favorite]:
        """
        Получает список избранных фильмов пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            list[Favorite]: Список избранных фильмов.
        """
        query = select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.added_at.desc())
        result = await self.db.execute(query)
        favorites = result.scalars().all()
        return list(favorites)

    async def remove_from_favorites(self, user_id: int, movie_id: int) -> bool:
        """
        Удаляет фильм из избранного пользователя.

        Args:
            user_id (int): ID пользователя.
            movie_id (int): ID фильма в TMDB.

        Returns:
            bool: True если удаление успешно, False если запись не найдена.
        """
        query = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.movie_id == movie_id
        )
        result = await self.db.execute(query)
        favorite = result.scalar_one_or_none()

        if not favorite:
            return False

        await self.db.delete(favorite)
        await self.db.commit()

        return True