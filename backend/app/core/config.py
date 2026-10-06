from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    frontend_origin: list[str] | str = "http://localhost:5173"
    google_client_id: str | None = None
    session_secret: str | None = None
    session_ttl_seconds: int = 28800
    cookie_secure: bool = False
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    gemini_timeout_seconds: int = 12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("frontend_origin", mode="before")
    @classmethod
    def parse_origins(cls, value: list[str] | str) -> list[str]:
        origins = value if isinstance(value, list) else value.split(",")
        cleaned = [origin.strip().rstrip("/") for origin in origins if origin.strip()]
        if not cleaned:
            raise ValueError("FRONTEND_ORIGIN must include at least one origin")
        if "*" in cleaned:
            raise ValueError("FRONTEND_ORIGIN must not contain '*'")
        return cleaned


@lru_cache
def get_settings() -> Settings:
    return Settings()
