from fastapi import Request, HTTPException
from redis_client import redis_client

async def rate_limit(request: Request):
    ip = request.client.host
    key = f"rate:{ip}:post_items"

    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)

    if count > 5:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    