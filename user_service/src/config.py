from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс для управления настройками приложения.

    Загружает переменные окружения из .env файла и предоставляет к ним доступ.

    Attributes:
        DATABASE_URL (str): URL для подключения к базе данных.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Время жизни JWT токена в минутах.
        ALGORITHM (str): Алгоритм шифрования для JWT токенов.
        SECRET_KEY (str): Секретный ключ для подписи JWT токенов.
    """
    DATABASE_URL: str

    # Время жизни JWT токена в минутах (по умолчанию 30 минут)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Алгоритм шифрования для JWT токенов (HS256 - самый распространенный)
    ALGORITHM: str = "HS256"

    # Секретный ключ для подписи JWT токенов (должен храниться в .env файле)
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
