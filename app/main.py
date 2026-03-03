# app/main.py
import asyncio
import logging
from aiohttp import web

from app.db import engine, Base, async_session
from app.routes import routes
from app.service import TicketService
import asyncio
from sqlalchemy.exc import OperationalError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticket_system")

# Middleware для передачи AsyncSession в обработчики
@web.middleware
async def db_session_middleware(request, handler):
    async with async_session() as session:
        request['db'] = session
        response = await handler(request)
        return response

async def on_startup(app):
    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created!")

    # Запуск фоновой задачи для закрытия тикетов waiting >24h
    async def close_waiting_tickets_task():
        while True:
            async with async_session() as session:
                service = TicketService(session)
                await service.close_waiting_tickets()
            await asyncio.sleep(3600)  # каждые 1 час

    app['ticket_closer'] = asyncio.create_task(close_waiting_tickets_task())
    logger.info("Background ticket closer started!")

async def on_cleanup(app):
    # Отменяем фоновые задачи
    app['ticket_closer'].cancel()
    try:
        await app['ticket_closer']
    except asyncio.CancelledError:
        logger.info("Background ticket closer stopped.")

async def init_app():
    app = web.Application(middlewares=[db_session_middleware])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.add_routes(routes)
    return app

if __name__ == "__main__":
    web.run_app(init_app(), port=8000)