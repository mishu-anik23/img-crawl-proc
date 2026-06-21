from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "nanoImage"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://nanoimage:secret@localhost:5432/nanoimage"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    gemini_api_key: str = ""
    replicate_api_token: str = ""

    storage_backend: str = "local"
    local_storage_path: str = "./storage"


@lru_cache
def get_settings() -> Settings:
    return Settings()
