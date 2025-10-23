from functools import lru_cache
from typing import Dict, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration for the OSINT manager service."""

    database_url: str = Field(
        default="sqlite:///./osint_manager.db",
        description="SQLAlchemy connection string for the analytics database.",
    )
    osint_refresh_interval: int = Field(
        default=60,
        description="Seconds between background OSINT refresh cycles.",
    )
    marketing_lookback_hours: int = Field(
        default=24,
        description="Hours of history to consider when computing marketing insights.",
    )
    ai_model: str = Field(
        default="gpt-synthetic",
        description="Identifier for the AI content generation backend.",
    )
    cms_credentials: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of CMS identifiers to API tokens or connection strings.",
    )
    enable_demo_data: bool = Field(
        default=True,
        description="Whether demo data should be produced on startup for visualization demos.",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
