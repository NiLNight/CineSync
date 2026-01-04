# Используем Python 3.12
FROM python:3.12-slim

# Оптимизация Python для работы в контейнере:
# - PYTHONDONTWRITEBYTECODE=1: не создавать .pyc файлы (мусор)
# - PYTHONUNBUFFERED=1: вывод логов сразу в консоль (важно для Docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (curl нужен для установки poetry)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# Копируем только файлы зависимостей (для кэширования слоев Docker)
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости (без dev-пакетов)
RUN poetry install --no-root --only main

# Копируем исходный код
COPY src/ ./src/

# Запускаем приложение через Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]