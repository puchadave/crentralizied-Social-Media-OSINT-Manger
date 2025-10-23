from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel


class SEOReportBase(SQLModel):
    url: str = Field(description="URL that was analysed.")
    title: Optional[str] = Field(default=None, description="HTML title tag content.")
    description: Optional[str] = Field(default=None, description="Meta description content.")
    keywords: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    score: float = Field(default=0.0, description="Composite SEO score between 0 and 100.")
    issues: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    recommendations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    lighthouse_metrics: Dict[str, float] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Synthetic performance metrics for the page.",
    )
    analysed_at: datetime = Field(default_factory=datetime.utcnow)


class SEOReport(SEOReportBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class SEOReportCreate(SEOReportBase):
    pass


class SEOReportRead(SEOReportBase):
    id: int


class MetadataPatch(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    og_image: Optional[str] = Field(default=None, description="OpenGraph image URL.")
