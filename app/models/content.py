from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel
from pydantic import BaseModel, Field


class ContentItemBase(SQLModel):
    channel: str = Field(description="Target channel such as twitter, linkedin, blog, etc.")
    title: str = Field(description="Internal title for the content asset.")
    body: str = Field(description="Primary content body or caption.")
    language: str = Field(default="de", description="Language of the content.")
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field(
        default="draft",
        description="Workflow status (draft, scheduled, published, archived).",
    )
    scheduled_for: Optional[datetime] = Field(default=None, description="Planned publication time.")
    metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class ContentItem(ContentItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentItemCreate(ContentItemBase):
    pass


class ContentItemRead(ContentItemBase):
    id: int
    created_at: datetime
    updated_at: datetime


class DispatchStatus(BaseModel):
    status: str
    reference: str
    delivered_at: datetime
    features: List[str] = Field(default_factory=list)
    metadata_applied: Optional[int] = None


class ContentDispatchResponse(BaseModel):
    item: ContentItemRead
    destinations: Dict[str, DispatchStatus]
