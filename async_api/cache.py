import json
from redis_client import redis_client

async def get_cached(key: str):
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

async def set_cached(key: str, data, ex: int = 60):
    await redis_client.set(key, json.dumps(data), ex=ex)

async def invalidate(key: str):
    await redis_client.delete(key)