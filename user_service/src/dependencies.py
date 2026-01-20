from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import User
from .database import get_db
from .schemas import TokenData

# OAuth2 схема для извлечения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Зависимость для получения текущего аутентифицированного пользователя.

    Извлекает JWT токен из заголовка Authorization, декодирует его,
    проверяет валидность и возвращает объект User из базы данных.

    Args:
        token (str): JWT токен из заголовка Authorization.
        db (AsyncSession): Сессия базы данных.

    Returns:
        User: Объект текущего пользователя.

    Raises:
        HTTPException: 401 если токен невалиден или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодируем JWT токен
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if email is None or user_id is None:
            raise credentials_exception

        token_data = TokenData(sub=email, user_id=user_id)
    except JWTError:
        raise credentials_exception

    # Загружаем пользователя из базы данных
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user
