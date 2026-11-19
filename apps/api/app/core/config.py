"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_JWT_SECRET = "dev-only-secret-change-me-0123456789abcdef"


def ensure_sqlite_directory(database_url: str) -> None:
    """SQLite creates the file, not the folder; make sure ``var/`` exists."""
    if database_url.startswith("sqlite") and "///" in database_url:
        raw_path = database_url.split("///", 1)[1]
        if raw_path and raw_path != ":memory:":
            Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Runtime settings. Every value can be overridden by an environment variable."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "My School API"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "sqlite+aiosqlite:///./var/dev.db"

    jwt_secret: str = Field(default=DEV_JWT_SECRET, min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 14
    refresh_token_remember_ttl_days: int = 30

    teacher_invite_code: str = ""
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    school_timezone: str = "Asia/Tehran"

    refresh_cookie_name: str = "myschool_refresh"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_for_startup(self) -> None:
        if self.is_production and self.jwt_secret == DEV_JWT_SECRET:
            raise RuntimeError("JWT_SECRET must be set to a strong secret in production")
        if self.is_production and not self.teacher_invite_code:
            raise RuntimeError("TEACHER_INVITE_CODE must be configured in production")


@lru_cache
def get_settings() -> Settings:
    return Settings()
