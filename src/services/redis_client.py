import redis.asyncio as redis
import json
from typing import Optional, Dict, Any

from src.conf.config import settings

redis_client: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    global redis_client
    if not redis_client:
        redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client

async def set_user_cache(user_id: int, user_data: Dict[str, Any], expire: int = 3600) -> None:
    redis = await get_redis()
    await redis.setex(f"user:{user_id}", expire, json.dumps(user_data))

async def get_user_cache(user_id: int) -> Optional[Dict[str, Any]]:
    redis = await get_redis()
    user_data = await redis.get(f"user:{user_id}")
    return json.loads(user_data) if user_data else None

async def delete_user_cache(user_id: int) -> None:
    redis = await get_redis()
    await redis.delete(f"user:{user_id}")
