"""Application settings using 12-factor environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core runtime
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    debug: bool = False

    # App metadata
    app_name: str = "Production AI Agent"
    app_version: str = "1.0.0"

    # Security
    agent_api_key: str = "dev-key-change-me"
    jwt_secret: str = "dev-jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    allowed_origins: str = "*"

    # Stateful dependencies
    redis_url: str = "redis://localhost:6379/0"

    # Guard rails
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0

    # LLM
    llm_model: str = "mock-llm"

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
