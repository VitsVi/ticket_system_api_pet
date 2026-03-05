import json

from aiohttp import web
from pydantic import ValidationError


async def validate_request(request, schema):
    """Парсиинг и валидация json с pydantic"""
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