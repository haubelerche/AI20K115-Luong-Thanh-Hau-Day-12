import time

import redis
from fastapi import Depends, HTTPException

from app.auth import verify_bearer_token
from app.config import settings

r = redis.from_url(settings.redis_url, decode_responses=True)


def check_rate_limit(user_id: str = Depends(verify_bearer_token)) -> None:
    """
    Sliding-window rate limiter backed by Redis sorted set.
    """
    window_seconds = 60
    now = time.time()
    key = f"rate:{user_id}"

    # Remove requests outside the current window.
    r.zremrangebyscore(key, 0, now - window_seconds)

    # Reject if request count in window already exceeds threshold.
    current = r.zcard(key)
    if current >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    request_id = f"{now}-{time.time_ns()}"
    r.zadd(key, {request_id: now})
    r.expire(key, window_seconds)
