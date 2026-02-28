# app/main.py
from aiohttp import web
from app.db.engine import engine, Base
from app.config import settings

async def on_startup(app):
    # Создание таблиц (для проверки)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")

async def init_app():
    app = web.Application()
    app.on_startup.append(on_startup)
    return app

if __name__ == "__main__":
    web.run_app(init_app(), port=8000)