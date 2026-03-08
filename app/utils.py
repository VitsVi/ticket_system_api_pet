import json

from aiohttp import web
from pydantic import ValidationError
from functools import wraps
import logging


async def validate_request(request, schema):
    """Парсиинг и валидация json с pydantic."""
    try:
        data = await request.json()
        return schema(**data)
    except ValidationError as e:
        missing_fields = [
            ".".join(str(x) for x in err["loc"])
            for err in e.errors()
            if err["type"] == "missing"
        ]
        raise web.HTTPBadRequest(
            text=json.dumps({"missing_fields": missing_fields}, ensure_ascii=False),
            content_type="application/json"
        )
    

def get_pagination_params(request, default_offset=0, default_limit=10, max_limit=100):
    """Проверка limit, offset параметров."""
    try:
        offset = int(request.query.get("offset", default_offset))
    except (TypeError, ValueError):
        offset = default_offset

    try:
        limit = int(request.query.get("limit", default_limit))
    except (TypeError, ValueError):
        limit = default_limit

    limit = min(limit, max_limit)
    offset = max(offset, 0)

    return offset, limit


def handle_errors(func):
    """Декоратор для обработки ошибок."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except web.HTTPException:
            raise
        except Exception as e:
            status = 400 if isinstance(e, ValueError) else 500
            return web.json_response(
                {"error": str(e)},
                status=status
            )
    return wrapper