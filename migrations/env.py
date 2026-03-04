from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine  # sync engine for Alembic
from alembic import context

# импорт Base из моделей
from app.db import Base
# импорт всех моделей, чтобы Base.metadata видел таблицы
from app.models import Client, Operator, Ticket, Message
# импорт настроек
from app.config import settings


# путь к приложению
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Настройка логирования через alembic.ini
fileConfig(config.config_file_name)

# ----------------------------
# Используем sync engine только для autogenerate
# ----------------------------
# DATABASE_URL с asyncpg нужно заменить на psycopg2
engine = create_engine(settings.DATABASE_URL_SYNC)

target_metadata = Base.metadata

# ----------------------------
# Функции для offline и online режима
# ----------------------------
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL_SYNC
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()