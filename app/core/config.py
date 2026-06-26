from functools import lru_cache

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "JobTrack CRM"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"
    SECRET_KEY: str = "change-this-super-secret-key-before-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = "postgresql+psycopg2://jobtrack:jobtrack@localhost:5434/jobtrack"
    REDIS_URL: str = "redis://localhost:6380/0"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] | list[str] = ["http://localhost:8000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
