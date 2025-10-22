from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel


class WebMetricBase(SQLModel):
    """Aggregierte Web- und App-Kennzahlen als Ersatz für Google Analytics."""

    source: str = Field(description="Quelle wie website, app, landingpage.")
    metric: str = Field(description="Kennzahl wie sessions, pageviews, conversions.")
    value: float = Field(description="Aggregierter Wert für das Zeitfenster.")
    period_start: datetime = Field(description="Beginn des Messzeitraums.")
    period_end: datetime = Field(description="Ende des Messzeitraums.")
    metadata: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))


class WebMetric(WebMetricBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class WebMetricCreate(WebMetricBase):
    pass


class WebMetricRead(WebMetricBase):
    id: int


class SearchMetricBase(SQLModel):
    """Realtime Search Console Ersatz."""

    query: str = Field(description="Suchanfrage oder Keyword.")
    clicks: float = Field(default=0.0)
    impressions: float = Field(default=0.0)
    ctr: float = Field(default=0.0, description="Click-Through-Rate in Prozent.")
    position: float = Field(description="Durchschnittliche Position.")
    period_start: datetime = Field()
    period_end: datetime = Field()
    metadata: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))


class SearchMetric(SearchMetricBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class SearchMetricCreate(SearchMetricBase):
    pass


class SearchMetricRead(SearchMetricBase):
    id: int
