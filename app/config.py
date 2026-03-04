from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int = 5432

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    APP_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",   # <-- указываем путь к .env
        env_file_encoding="utf-8",
        extra=None
    )

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def DATABASE_URL(self) -> str:
        # для asyncpg в контейнере
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        # для Alembic/psycopg2 локально
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()