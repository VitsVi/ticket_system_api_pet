from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

Base = declarative_base()

# async engine для приложения
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# async session factory
AsyncSession = async_sessionmaker(
    engine, expire_on_commit=False
)