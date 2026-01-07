from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from .models import User
from .schemas import UserCreate
from .security import get_password_hash, verify_password


class UserService:
    """
    Сервис для управления пользователями.

    Реализует бизнес-логику работы с пользователями: регистрацию, аутентификацию.
    Работает с базой данных через асинхронную сессию SQLAlchemy.

    Attributes:
        db (AsyncSession): Сессия базы данных для выполнения запросов.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

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