import json
from typing import Any


class Cache:
    """Thin wrapper around any redis-like client (works with arq's ArqRedis too)."""

    def __init__(self, redis):
        self._redis = redis

    async def get_json(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value: Any, ttl: int) -> None:
        await self._redis.set(key, json.dumps(value), ex=ttl)
