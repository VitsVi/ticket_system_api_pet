import redis.asyncio as aioredis

from app.config import settings


redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


async def get_ticket_counts():
    return await redis.hgetall("ticket_counts")


async def update_ticket_count(status: str, delta: int):
    await redis.hincrby("ticket_counts", status, delta)