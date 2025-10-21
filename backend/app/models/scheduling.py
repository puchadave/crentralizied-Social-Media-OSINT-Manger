"""Pydantic models for scheduling endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from .content import ContentPiece
from ..utils.time import ensure_aware_utc, utc_now


class SchedulePostRequest(BaseModel):
    """Request payload for scheduling generated content."""

    content: ContentPiece = Field(..., description="Content that should be published.")
    scheduled_time: datetime = Field(
        ..., description="Timestamp (ISO8601) when the post should be published."
    )
    platforms: list[str] = Field(
        ..., min_length=1, description="List of platforms where the post should be published."
    )
    campaign: Optional[str] = Field(
        default=None, description="Optional campaign identifier for grouping posts."
    )

    @field_validator("scheduled_time", mode="before")
    @classmethod
    def _ensure_timezone(cls, value):
        return ensure_aware_utc(value)


class ScheduledPost(BaseModel):
    """Represents a stored scheduled post."""

    id: str = Field(..., description="Unique identifier for the scheduled post entry.")
    status: Literal["scheduled", "sent", "failed"] = Field(
        default="scheduled", description="Current state of the scheduled post."
    )
    created_at: datetime = Field(
        default_factory=utc_now, description="Timestamp when the entry was created."
    )
    updated_at: datetime = Field(
        default_factory=utc_now, description="Timestamp when the entry was last updated."
    )
    content: ContentPiece
    scheduled_time: datetime
    platforms: list[str]
    campaign: Optional[str] = None


class ScheduledPostCollection(BaseModel):
    """Collection wrapper for scheduled posts."""

    items: list[ScheduledPost]
