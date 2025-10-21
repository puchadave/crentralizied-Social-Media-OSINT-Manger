"""Pydantic models for OSINT monitoring endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from ..utils.time import ensure_aware_utc, utc_now


class Interaction(BaseModel):
    """Represents a single interaction captured during OSINT monitoring."""

    user_id: str = Field(..., description="Unique identifier for the user who interacted.")
    user_display_name: Optional[str] = Field(
        default=None, description="Human readable display name of the user."
    )
    interaction_type: Literal["comment", "repost", "like"] = Field(
        ..., description="Type of engagement detected for the monitored post."
    )
    content: Optional[str] = Field(
        default=None, description="Optional textual content (for comments/reposts)."
    )
    timestamp: datetime = Field(
        default_factory=utc_now,
        description="Timestamp when the interaction occurred.",
    )
    in_reply_to: Optional[str] = Field(
        default=None,
        description="Identifier of another user the interaction replied to (for comment threads).",
    )
    follower_count: Optional[int] = Field(
        default=None,
        description="Approximate follower count of the user for reach estimations.",
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def _ensure_timezone(cls, value):
        return ensure_aware_utc(value)


class InteractionIngestRequest(BaseModel):
    """Payload for storing monitored interactions."""

    post_id: str = Field(..., description="Identifier of the monitored post.")
    platform: str = Field(..., description="Platform the interactions belong to.")
    interactions: list[Interaction] = Field(
        default_factory=list, description="Captured interactions for the post."
    )


class InteractionSummary(BaseModel):
    """Aggregate metrics for a monitored post."""

    post_id: str
    platform: str
    total_interactions: int
    unique_users: int
    comments: int
    reposts: int
    likes: int
    estimated_reach: int


class NetworkNode(BaseModel):
    """Node entry for a network graph representation."""

    id: str
    label: str
    type: Literal["post", "user"]


class NetworkEdge(BaseModel):
    """Edge entry for a network graph representation."""

    source: str
    target: str
    weight: int = 1


class NetworkGraph(BaseModel):
    """Network data structure containing nodes and edges."""

    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
