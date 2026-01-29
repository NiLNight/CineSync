FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости для сборки если нужно
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/dist/lists/*

# Устанавливаем poetry
RUN pip install poetry

# Копируем файлы проекта
COPY pyproject.toml .
# poetry.lock может отсутствовать при первом создании, игнорируем если нет
COPY poetry.lock* ./

# Настраиваем poetry: не создавать виртуальное окружение во время сборки контейнера
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY src/ ./src/

# Запуск приложения
CMD ["python", "src/main.py"]
