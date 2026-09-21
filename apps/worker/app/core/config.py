from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = Field(default="", alias="DATABASE_URL")
    worker_auth_secret: str = Field(default="", alias="WORKER_AUTH_SECRET")
    worker_concurrency: int = Field(default=2, alias="WORKER_CONCURRENCY")
    scan_timeout_seconds: int = Field(default=120, alias="SCAN_TIMEOUT_SECONDS")
    max_upload_size_bytes: int = Field(default=10 * 1024 * 1024, alias="MAX_UPLOAD_SIZE_BYTES")
    max_archive_size_bytes: int = Field(default=50 * 1024 * 1024, alias="MAX_ARCHIVE_SIZE_BYTES")
    supabase_url: str = Field(default="", alias="NEXT_PUBLIC_SUPABASE_URL")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
