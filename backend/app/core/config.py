"""Application configuration settings."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

    project_name: str = Field(
        default="Centralized Social Media OSINT Manager",
        description="Human friendly project name exposed in the API docs.",
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_KEY",
        description="API key used to authenticate against the OpenAI API.",
    )
    openai_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the OpenAI REST API.",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Default model identifier used for content generation.",
    )

@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings()


settings = get_settings()
