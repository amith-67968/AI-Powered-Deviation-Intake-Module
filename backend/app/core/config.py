from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Supabase PostgreSQL is the single supported runtime database. It must be
    # supplied from backend/.env or the deployment environment; no local fallback.
    database_url: str | None = None
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 10
    max_input_chars: int = 60000

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
