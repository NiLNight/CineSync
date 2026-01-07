from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс для управления настройками приложения.

    Загружает переменные окружения из .env файла и предоставляет к ним доступ.

    Attributes:
        DATABASE_URL (str): URL для подключения к базе данных.
    """
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Экземпляр настроек для использования во всем приложении
settings = Settings()