from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel


class OSINTEventBase(SQLModel):
    platform: str = Field(description="Source platform of the OSINT event.")
    content_id: str = Field(description="Platform-specific identifier for the content.")
    author: Optional[str] = Field(default=None, description="Handle or author of the content.")
    text: str = Field(description="Normalised textual content extracted from the post.")
    language: str = Field(default="en", description="Detected language of the content.")
    sentiment: float = Field(default=0.0, description="Sentiment score in the range [-1, 1].")
    engagement_score: float = Field(
        default=0.0,
        description="Weighted engagement score derived from reactions, shares and comments.",
    )
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of normalised tags extracted from the content.",
    )
    captured_at: datetime = Field(default_factory=datetime.utcnow, description="Time of ingestion.")
    event_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the original social media event.",
    )


class OSINTEvent(OSINTEventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class OSINTEventCreate(OSINTEventBase):
    pass


class OSINTEventRead(OSINTEventBase):
    id: int


class OSINTSummary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    period_start: datetime = Field(default_factory=datetime.utcnow)
    period_end: datetime = Field(default_factory=datetime.utcnow)
    platform: str = Field(description="Platform the summary relates to.")
    mention_volume: int = Field(default=0)
    average_sentiment: float = Field(default=0.0)
    top_tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
