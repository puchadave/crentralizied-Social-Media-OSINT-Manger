"""Utility helpers for working with timezone aware timestamps."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Union


def utc_now() -> datetime:
    """Return the current time as timezone aware UTC datetime."""

    return datetime.now(timezone.utc)


def ensure_aware_utc(value: Union[datetime, str]) -> datetime:
    """Ensure that a datetime value is timezone aware and normalised to UTC."""

    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
