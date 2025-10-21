"""Pydantic models for content generation endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from ..utils.time import utc_now

class ContentGenerationRequest(BaseModel):
    """User request for generating social media or newsletter content."""

    topic: str = Field(..., description="Topic or campaign theme for the generated content.")
    platform: str = Field(
        ..., description="Target platform such as LinkedIn, Twitter, Instagram, etc."
    )
    tone: str = Field(
        default="informational",
        description="Desired tone of voice for the generated content (e.g. friendly, formal).",
    )
    language: str = Field(
        default="de",
        description="Language for the generated content output (e.g. 'de', 'en').",
    )
    audience: Optional[str] = Field(
        default=None,
        description="Optional audience description to provide additional context.",
    )
    format: Literal["post", "newsletter", "thread"] = Field(
        default="post",
        description="Specifies which type of content should be generated.",
    )


class ContentSection(BaseModel):
    """Structured section of generated content."""

    heading: Optional[str] = Field(default=None, description="Title for the section if available.")
    body: str = Field(..., description="Text body of the section.")


class ContentPiece(BaseModel):
    """A generated content artefact (post, newsletter, etc.)."""

    title: Optional[str] = Field(default=None, description="Title of the content piece if relevant.")
    summary: Optional[str] = Field(
        default=None, description="Optional summary or abstract for the generated content."
    )
    body: str = Field(
        ..., description="Primary text that should be published to the social media platform."
    )
    hashtags: list[str] = Field(
        default_factory=list, description="List of suggested hashtags for the post."
    )
    call_to_action: Optional[str] = Field(
        default=None,
        description="Suggested call-to-action sentence or question.",
    )
    sections: list[ContentSection] = Field(
        default_factory=list,
        description="Structured sections for newsletter style outputs.",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the piece was generated.",
    )


class ContentGenerationMetadata(BaseModel):
    """Metadata returned alongside generated content."""

    model: str = Field(..., description="Model identifier used to generate the content.")
    prompt: str = Field(..., description="Prompt that was sent to the LLM.")
    used_fallback: bool = Field(
        default=False,
        description="Indicates whether a deterministic fallback generator was used.",
    )
    raw_response: Optional[dict[str, Any]] = Field(
        default=None, description="Optional raw provider response for debugging."
    )


class ContentGenerationResponse(BaseModel):
    """Response payload for content generation requests."""

    request: ContentGenerationRequest
    content: ContentPiece
    metadata: ContentGenerationMetadata
