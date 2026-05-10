from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    db_pool_size: int = 1
    db_max_overflow: int = 0
    db_pool_timeout_s: int = 30
    db_disable_pooling: bool = False
    pipeline_use_langgraph: bool = False
    app_env: str = "development"
    frontend_cors_origins: list[str] | str = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
