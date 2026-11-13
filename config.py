from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://kutana:kutana@localhost:5432/kutana"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24 * 7
    fernet_key: str
    cors_origins: list[str] = ["http://localhost:5173"]

    anthropic_api_key: str = ""
    chat_model: str = "claude-haiku-5-5"
    scoring_model: str = "claude-sonnet-5-5"

    max_profiler_messages: int = 10          # matches the "10 Tokens" bar in the UI
    session_ttl_hours: int = 24              # abandoned chats are purged (ODPC data minimisation)
    free_daily_swipes: int = 15
    free_visible_matches: int = 2            # free users see top N; the rest are "locked"

    public_base_url: str = "http://localhost:8000"
    mpesa_base_url: str = "https://sandbox.safaricom.co.ke"
    mpesa_consumer_key: str = ""
    mpesa_consumer_secret: str = ""
    mpesa_shortcode: str = "174379"
    mpesa_passkey: str = ""
    mpesa_callback_secret: str = "change-me"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

PLANS = {"black_monthly": {"amount_kes": 390, "days": 30}}
