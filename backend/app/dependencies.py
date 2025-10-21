"""Dependency definitions for FastAPI routes."""
from __future__ import annotations

from functools import lru_cache

from .core.config import get_settings
from .services.content_generator import ContentGeneratorService
from .services.osint import OsintService
from .services.scheduler import SchedulerService


@lru_cache
def get_content_generator_service() -> ContentGeneratorService:
    """Return a cached instance of :class:`ContentGeneratorService`."""

    return ContentGeneratorService(get_settings())


_scheduler_service = SchedulerService()
_osint_service = OsintService()


def get_scheduler_service() -> SchedulerService:
    """Return a process-wide scheduler service instance."""

    return _scheduler_service


def get_osint_service() -> OsintService:
    """Return a process-wide OSINT service instance."""

    return _osint_service
