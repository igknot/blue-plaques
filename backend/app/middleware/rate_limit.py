from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from ..core.cache import redis_client

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window = 60  # seconds

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current = redis_client.get(key)
            if current is None:
                redis_client.setex(key, self.window, 1)
            else:
                count = int(current)
                if count >= self.requests_per_minute:
                    raise HTTPException(status_code=429, detail="Too many requests")
                redis_client.incr(key)
        except Exception:
            pass  # Fail open if Redis is down
        
        return await call_next(request)
