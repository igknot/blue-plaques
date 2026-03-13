import redis
from ..config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_cache(key: str):
    return redis_client.get(key)

def set_cache(key: str, value: str, expire: int = 300):
    redis_client.setex(key, expire, value)

def delete_cache(key: str):
    redis_client.delete(key)

def clear_pattern(pattern: str):
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
