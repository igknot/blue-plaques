import redis
from ..config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True) if settings.REDIS_URL else None

def get_cache(key: str):
    return redis_client.get(key) if redis_client else None

def set_cache(key: str, value: str, expire: int = 300):
    if redis_client:
        redis_client.setex(key, expire, value)

def delete_cache(key: str):
    if redis_client:
        redis_client.delete(key)

def clear_pattern(pattern: str):
    if redis_client:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
