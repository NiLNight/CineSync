from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .schemas import UserCreate, UserResponse, Token
from .service import UserService
from .config import settings
from .security import create_access_token
app = FastAPI(title="User Service")


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
