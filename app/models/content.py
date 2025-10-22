from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field as SQLField, SQLModel
from pydantic import BaseModel, Field as PydanticField


class ContentItemBase(SQLModel):
    channel: str = SQLField(description="Target channel such as twitter, linkedin, blog, etc.")
    title: str = SQLField(description="Internal title for the content asset.")
    body: str = SQLField(description="Primary content body or caption.")
    language: str = SQLField(default="de", description="Language of the content.")
    tags: List[str] = SQLField(default_factory=list, sa_column=Column(JSON))
    status: str = SQLField(
        default="draft",
        description="Workflow status (draft, scheduled, published, archived).",
    )
    scheduled_for: Optional[datetime] = SQLField(
        default=None, description="Planned publication time."
    )
    metadata_: Dict[str, Any] = SQLField(
        default_factory=dict,
        alias="metadata",
        sa_column=Column(JSON),
    )

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.metadata_

    @metadata.setter
    def metadata(self, value: Dict[str, Any]) -> None:
        self.metadata_ = value


class ContentItem(ContentItemBase, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)


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
    features: List[str] = PydanticField(default_factory=list)
    metadata_applied: Optional[int] = None


class ContentDispatchResponse(BaseModel):
    item: ContentItemRead
    destinations: Dict[str, DispatchStatus]
