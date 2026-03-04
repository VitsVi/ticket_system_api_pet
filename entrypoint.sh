#!/bin/sh
set -e

# Ждём, пока база станет доступна
echo "Waiting for database at $DB_HOST:$DB_PORT..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  sleep 1
done
echo "Database is ready."

# Создаем ревизию, если нет ни одной
if [ -z "$(ls -A /app/migrations/versions 2>/dev/null)" ]; then
  echo "No Alembic revisions found. Creating initial revision..."
  alembic revision --autogenerate -m "initial tables"
else
  echo "Alembic revisions already exist."
fi

# Применяем все миграции
echo "Applying Alembic migrations..."
alembic upgrade head

# Запускаем приложение
echo "Starting application..."
exec python -m app.main