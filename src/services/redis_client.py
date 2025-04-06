import redis.asyncio as redis

from src.conf.config import settings

redis_client: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    global redis_client
    if not redis_client:
        redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client
