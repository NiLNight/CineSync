import json
import logging
import httpx
from fastapi import HTTPException
from redis.asyncio import Redis

from .config import settings

logger = logging.getLogger("uvicorn")


class MovieService:
    """
    Сервис для работы с фильмами. Реализует поиск фильмов с кэшированием результатов.

    Attributes:
        redis (Redis): Асинхронный клиент Redis для кэширования.
        client (httpx.AsyncClient): Асинхронный HTTP-клиент для запросов к TMDB API.
    """
    def __init__(self, redis: Redis, http_client: httpx.AsyncClient):
        """
        Инициализирует сервис с внедренными зависимостями.

        Args:
            redis (Redis): Клиент Redis для кэширования.
            http_client (httpx.AsyncClient): HTTP-клиент для запросов к API.
        """
        self.redis = redis
        self.client = http_client

    async def search_movies(self, query: str) -> list[dict]:
        """
        Выполняет поиск фильмов по запросу с использованием кэширования.

        Алгоритм работы:
        1. Нормализация поискового запроса и формирование ключа кэша
        2. Проверка наличия результатов в кэше Redis
        3. Если кэш отсутствует - запрос к TMDB API
        4. Сохранение результатов в кэш с TTL 5 минут

        Args:
            query (str): Поисковый запрос (название фильма).

        Returns:
            list[dict]: Список словарей с информацией о фильмах.

        Raises:
            HTTPException: Если не удалось выполнить запрос к TMDB API.
        """
        # Нормализация ключа: приведение к нижнему регистру и удаление пробелов
        cache_key = f"movie_search:{query.lower().strip()}"

        # Попытка получить данные из кэша Redis
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info(f"🟢 Cache HIT for '{query}'")
            return json.loads(cached)

        # Если кэш отсутствует, выполняем запрос к внешнему API
        logger.info(f"🟡 Cache MISS for '{query}' -> Calling TMDB")
        try:
            response = await self.client.get(
                "/search/movie",
                params={
                    "query": query,
                    "api_key": settings.TMDB_API_KEY,
                    "language": "ru-RU"
                }
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            # Логируем ошибку и пробрасываем HTTPException для клиента
            logger.error(f"TMDB Error: {e}")
            raise HTTPException(status_code=502, detail="Movie provider unavailable")

        data = response.json().get("results", [])

        # Сохраняем результаты в кэш, только если они не пустые
        # TTL 300 секунд (5 минут) для актуальности данных
        if data:
            await self.redis.set(cache_key, json.dumps(data), ex=300)

        return data