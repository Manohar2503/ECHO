import redis
import os
import json
from typing import Any, Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()
    USE_REDIS = True
except:
    USE_REDIS = False
    cache = {}

def set_cache(key: str, value: Any, ttl: int = 3600):
    if USE_REDIS:
        redis_client.setex(key, ttl, json.dumps(value))
    else:
        cache[key] = value

def get_cache(key: str) -> Optional[Any]:
    if USE_REDIS:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    else:
        return cache.get(key)

def delete_cache(key: str):
    if USE_REDIS:
        redis_client.delete(key)
    else:
        cache.pop(key, None)