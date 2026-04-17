import json
import logging
import os
import signal
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

import redis
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import create_access_token, verify_api_key, verify_bearer_token
from app.config import settings
from app.cost_guard import check_budget
from app.rate_limiter import check_rate_limit
from utils.mock_llm import ask as mock_llm_ask

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.redis_url, decode_responses=True)
start_time = time.time()
is_ready = False
_openai_client: Optional[object] = None


def get_openai_client() -> Optional[object]:
    """Return OpenAI client if package + API key are available."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        logger.warning("OPENAI_API_KEY is set but `openai` package is missing; using mock LLM")
        return None

    _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def llm_ask(question: str) -> str:
    """Use OpenAI when available; fallback to mock LLM."""
    client = get_openai_client()
    if client is None:
        return mock_llm_ask(question)

    model = settings.llm_model if settings.llm_model != "mock-llm" else "gpt-4o-mini"
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            temperature=0.2,
        )
        answer = resp.choices[0].message.content if resp.choices else ""
        return answer or "I could not generate a response."
    except Exception as exc:  # pragma: no cover - fallback guard
        logger.warning("OpenAI request failed (%s); fallback to mock LLM", exc)
        return mock_llm_ask(question)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class AskResponse(BaseModel):
    user_id: str
    question: str
    answer: str
    history_items: int
    model: str
    timestamp: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    global is_ready
    logger.info(json.dumps({"event": "startup", "app": settings.app_name}))
    is_ready = True
    yield
    is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[v.strip() for v in settings.allowed_origins.split(",") if v.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = time.time()
    response = await call_next(request)
    logger.info(
        json.dumps(
            {
                "event": "request",
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.time() - started) * 1000, 2),
            }
        )
    )
    return response


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "auth_flow": "POST /auth/token with X-API-Key, then use Bearer token on /ask",
    }


@app.post("/auth/token", response_model=TokenResponse)
def issue_token(user_id: str = Depends(verify_api_key)):
    token = create_access_token(user_id=user_id)
    return TokenResponse(access_token=token, expires_in_seconds=settings.jwt_exp_minutes * 60)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - start_time, 2),
    }


@app.get("/ready")
def ready():
    if not is_ready:
        raise HTTPException(status_code=503, detail="Application is starting up")
    try:
        redis_client.ping()
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=503, detail=f"Redis not ready: {exc}") from exc
    return {"status": "ready"}


@app.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    user_id: str = Depends(verify_bearer_token),
    _rate_limit: None = Depends(check_rate_limit),
    _budget: None = Depends(check_budget),
):
    history_key = f"history:{user_id}"
    history = redis_client.lrange(history_key, 0, -1)
    answer = llm_ask(body.question)

    redis_client.rpush(history_key, json.dumps({"q": body.question, "a": answer}))
    redis_client.ltrim(history_key, -20, -1)

    return AskResponse(
        user_id=user_id,
        question=body.question,
        answer=answer,
        history_items=len(history) + 1,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _handle_sigterm(signum, _frame):
    logger.info(json.dumps({"event": "signal_received", "signum": signum}))


signal.signal(signal.SIGTERM, _handle_sigterm)
signal.signal(signal.SIGINT, _handle_sigterm)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        timeout_graceful_shutdown=30,
    )
