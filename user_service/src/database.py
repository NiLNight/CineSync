from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings

# Создаем асинхронный движок для подключения к базе данных
# Параметр echo=True включает логирование SQL-запросов (используется только для отладки)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

# Фабрика для создания асинхронных сессий работы с базой данных
# expire_on_commit=False позволяет использовать объекты после коммита транзакции
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Предоставляет общую функциональность для декларативного объявления моделей.
    Все модели в приложении должны наследоваться от этого класса.
    """
    pass


async def get_db():
    """
    Генератор зависимостей для FastAPI.

    Создает и предоставляет асинхронную сессию базы данных для каждого запроса.
    После завершения обработки запроса сессия автоматически закрывается.

    Yields:
        AsyncSession: Асинхронная сессия для работы с базой данных.
    """
    async with async_session_maker() as session:
        yield session