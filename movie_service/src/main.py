from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Depends, HTTPException
from redis.asyncio import Redis

from .config import settings
from .service import MovieService
from .schemas import MovieSearchResponse, MovieDetail

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


@app.get("/movies/{movie_id}", response_model=MovieDetail)
async def get_movie_details(movie_id: int, service: MovieService = Depends(get_service)):
    """
    Получает детальную информацию о фильме по его ID.

    Этот эндпоинт используется для межсервисного взаимодействия,
    когда User Service нужно проверить существование фильма и получить его данные.

    Args:
        movie_id (int): Уникальный идентификатор фильма в TMDB.
        service (MovieService): Сервис для работы с фильмами, внедряется через зависимость.

    Returns:
        MovieDetail: Детальная информация о фильме.

    Raises:
        HTTPException: 404 если фильм не найден, 502 если TMDB недоступен.
    """
    movie = await service.get_movie_by_id(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    return movie
