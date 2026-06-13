# app/core/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Dental Mind API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Environment variables (required)
    DATABASE_URL: str
    DATABASE_URL_LOCAL: str
    GROQ_API_KEY: str

    # Optional environment variables
    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    The .env file is loaded only once.
    """
    return Settings()