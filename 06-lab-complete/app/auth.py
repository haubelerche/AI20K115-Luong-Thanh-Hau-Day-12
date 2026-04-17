from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException

from app.config import settings


def verify_api_key(x_api_key: str = Header(default="", alias="X-API-Key")) -> str:
    """
    Validate caller API key and return a stable user_id.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    if x_api_key != settings.agent_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return "lab-user"


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_bearer_token(authorization: str = Header(default="", alias="Authorization")) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject")
    return str(user_id)
