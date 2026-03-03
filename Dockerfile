# Dockerfile
FROM python:3.11-slim

# Устанавливаем системные зависимости для asyncpg, PostgreSQL и сборки Python пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Переменные окружения (можно потом перекрывать через docker-compose)
ENV DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ticket_db
ENV REDIS_URL=redis://redis:6379

# Команда запуска: применяем миграции и стартуем API
CMD alembic upgrade head && python -m app.main