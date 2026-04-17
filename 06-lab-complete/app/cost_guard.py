from datetime import datetime
import redis
from fastapi import Depends, HTTPException

from app.auth import verify_bearer_token
from app.config import settings

r = redis.from_url(settings.redis_url, decode_responses=True)


def check_budget(user_id: str = Depends(verify_bearer_token)) -> None:
    """
    Enforce per-user monthly budget in USD.
    """
    estimated_cost = 0.01  # Flat estimate for this lab.
    month_key = datetime.utcnow().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"

    current_spend = float(r.get(key) or 0.0)
    if current_spend + estimated_cost > settings.monthly_budget_usd:
        raise HTTPException(status_code=402, detail="Monthly budget exceeded")

    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)
