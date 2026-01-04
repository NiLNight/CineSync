from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Конфигурация приложения. Загружает переменные окружения из .env файла.

    Attributes:
        TMDB_API_KEY (str): API-ключ для доступа к TMDB API.
        TMDB_BASE_URL (str): Базовый URL TMDB API. По умолчанию "https://api.themoviedb.org/3".
        REDIS_HOST (str): Хост Redis-сервера.
        REDIS_PORT (int): Порт Redis-сервера.
    """
    TMDB_API_KEY: str
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"

    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()