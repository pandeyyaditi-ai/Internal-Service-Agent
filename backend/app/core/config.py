"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Central configuration for the Internal Service Agent."""

    # App
    APP_NAME: str = "Internal Service Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Google Gemini
    GEMINI_API_KEY: str = ""

    # SQLite Database
    SQLITE_DB_PATH: str = "service_agent.db"

    # Security
    JWT_SECRET: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Singleton settings instance
settings = Settings()
