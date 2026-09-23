from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    github_token: str
    webhook_secret: str
    database_url: str = "sqlite+aiosqlite:///./reviews.db"
    redis_url: str = "redis://localhost:6379"
    environment: str = "development"
    diff_cache_ttl_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
