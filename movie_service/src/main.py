from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Depends
from redis.asyncio import Redis

from .config import settings
from .service import MovieService
from .schemas import MovieSearchResponse

# Глобальный словарь для хранения подключений к внешним ресурсам
resources = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения FastAPI.

    Выполняет инициализацию подключений к Redis и HTTP-клиенту при запуске
    и корректно закрывает их при завершении работы приложения.

    Args:
        app (FastAPI): Экземпляр FastAPI приложения.

    Yields:
        None: Передает управление обратно в приложение.
    """
    # Инициализация подключений при запуске приложения
    resources["redis"] = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    resources["http_client"] = httpx.AsyncClient(base_url=settings.TMDB_BASE_URL)

    yield

    # Корректное закрытие подключений при завершении работы
    await resources["http_client"].aclose()
    await resources["redis"].aclose()


app = FastAPI(title="Movie Service", lifespan=lifespan)


# Dependency Injection
def get_service() -> MovieService:
    """
    Фабрика для создания экземпляра MovieService.

    Возвращает экземпляр сервиса с внедренными зависимостями (Redis и HTTP-клиент).

    Returns:
        MovieService: Экземпляр сервиса для работы с фильмами.
    """
    return MovieService(
        redis=resources["redis"],
        http_client=resources["http_client"]
    )


@app.get("/search", response_model=MovieSearchResponse)
async def search_handler(query: str, service: MovieService = Depends(get_service)):
    """
    Обрабатывает запрос на поиск фильмов.

    Args:
        query (str): Поисковый запрос (название фильма).
        service (MovieService): Сервис для работы с фильмами, внедряется через зависимость.

    Returns:
        MovieSearchResponse: Результаты поиска фильмов.

    Raises:
        HTTPException: Если возникает ошибка при обращении к внешнему API.
    """
    results = await service.search_movies(query)
    return {"results": results}
