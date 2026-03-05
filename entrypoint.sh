#!/bin/sh
set -e

if [ -z "$(ls -A /app/migrations/versions 2>/dev/null)" ]; then
  echo "No Alembic revisions found. Creating initial revision..."
  alembic revision --autogenerate -m "initial tables"
else
  echo "Alembic revisions already exist."
fi

echo "Applying Alembic migrations..."
alembic upgrade head

echo "Starting application..."
exec python -m app.main