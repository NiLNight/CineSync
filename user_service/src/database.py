from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings

# 1. Создаем движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # Логируем SQL запросы (для отладки)
)

# 2. Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3. Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# 4. Зависимость для FastAPI
async def get_db():
    async with async_session_maker() as session:
        yield session