from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from .database import get_db
from .schemas import UserCreate, UserResponse, Token, FavoriteCreate, FavoriteResponse
from .service import UserService
from .config import settings
from .security import create_access_token
from .dependencies import get_current_user
from .models import User

# Глобальный словарь для хранения HTTP клиента
resources = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.

    Создает HTTP клиент для межсервисных запросов при запуске
    и корректно закрывает его при завершении.
    """
    # Инициализация HTTP клиента
    resources["http_client"] = httpx.AsyncClient()

    # Подключение к RabbitMQ
    from .events import publisher
    await publisher.connect()

    yield

    # Закрытие клиентов
    await resources["http_client"].aclose()
    await publisher.close()


app = FastAPI(title="User Service", lifespan=lifespan)


@app.post("/register", response_model=UserResponse)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Регистрирует нового пользователя в системе.

    Args:
        user_in (UserCreate): Данные для регистрации пользователя.
        db (AsyncSession): Сессия базы данных, автоматически инжектируется.

    Returns:
        UserResponse: Информация о зарегистрированном пользователе.

    Raises:
        HTTPException: Если email уже зарегистрирован (код 400).
    """
    service = UserService(db)
    return await service.create_user(user_in)


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """
    Аутентифицирует пользователя и выдает JWT токен.

    Использует стандартную форму OAuth2, где username соответствует email.

    Args:
        form_data (OAuth2PasswordRequestForm): Форма с данными для входа.
        db (AsyncSession): Сессия базы данных, автоматически инжектируется.

    Returns:
        Token: JWT токен доступа с типом "bearer".

    Raises:
        HTTPException: Если email или пароль неверны (код 401).
    """
    service = UserService(db)

    # form_data.username - email
    user = await service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаем токен с заданным временем жизни из настроек
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/me/favorites", response_model=FavoriteResponse)
async def add_favorite(
        favorite_in: FavoriteCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Добавляет фильм в избранное текущего пользователя.

    Требует аутентификации через JWT токен.

    Args:
        favorite_in (FavoriteCreate): ID фильма для добавления.
        current_user (User): Текущий пользователь из JWT токена.
        db (AsyncSession): Сессия базы данных.

    Returns:
        FavoriteResponse: Информация о добавленном избранном фильме.

    Raises:
        HTTPException: 404 если фильм не найден, 400 если уже в избранном.
    """
    service = UserService(db, http_client=resources["http_client"])
    return await service.add_to_favorites(current_user.id, favorite_in.movie_id)


@app.get("/users/me/favorites", response_model=list[FavoriteResponse])
async def get_favorites(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Получает список избранных фильмов текущего пользователя.

    Требует аутентификации через JWT токен.

    Args:
        current_user (User): Текущий пользователь из JWT токена.
        db (AsyncSession): Сессия базы данных.

    Returns:
        list[FavoriteResponse]: Список избранных фильмов.
    """
    service = UserService(db)
    return await service.get_user_favorites(current_user.id)


@app.delete("/users/me/favorites/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
        movie_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Удаляет фильм из избранного текущего пользователя.

    Требует аутентификации через JWT токен.

    Args:
        movie_id (int): ID фильма для удаления из избранного.
        current_user (User): Текущий пользователь из JWT токена.
        db (AsyncSession): Сессия базы данных.

    Raises:
        HTTPException: 404 если фильм не найден в избранном.
    """
    service = UserService(db)
    success = await service.remove_from_favorites(current_user.id, movie_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
