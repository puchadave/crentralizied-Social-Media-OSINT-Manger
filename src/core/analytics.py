"""Analytics helpers for KPI aggregation and visualization."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import cos, sin
from typing import Iterable


@dataclass(slots=True)
class KPI:
    name: str
    value: float
    unit: str
    trend_percentage: float


@dataclass(slots=True)
class TimeSeriesPoint:
    timestamp: datetime
    value: float


@dataclass(slots=True)
class RealtimeMetric:
    name: str
    value: float
    unit: str
    trend_percentage: float


class AnalyticsService:
    """Provides computed KPIs and historic trends."""

    def __init__(self) -> None:
        self._network_targets = {
            "Facebook": 1200,
            "LinkedIn": 800,
            "Instagram": 1750,
            "YouTube": 3400,
            "Mastodon": 420,
            "Reddit": 960,
            "X": 2100,
        }
        self._bootstrap = datetime.utcnow()

    def get_kpis(self) -> list[KPI]:
        return [
            KPI(name="Engagement", value=68.3, unit="%", trend_percentage=4.2),
            KPI(name="Conversions", value=312, unit="", trend_percentage=8.5),
            KPI(name="Reach", value=12850, unit="Impr.", trend_percentage=-3.1),
            KPI(name="Customer Satisfaction", value=4.6, unit="/5", trend_percentage=1.4),
        ]

    def engagement_timeseries(self, days: int = 14) -> list[TimeSeriesPoint]:
        base = datetime.utcnow()
        return [
            TimeSeriesPoint(timestamp=base - timedelta(days=offset), value=52 + (offset % 5) * 2.5)
            for offset in reversed(range(days))
        ]

    def network_targets(self) -> dict[str, int]:
        return dict(self._network_targets)

    def aggregate_replies(self, replies: Iterable[int]) -> float:
        values = list(replies)
        if not values:
            return 0.0
        total = sum(values)
        return total / len(values)

    def web_realtime_metrics(self) -> list[RealtimeMetric]:
        """Simulated real-time KPIs for the owned website."""

        now = datetime.utcnow()
        elapsed_minutes = (now - self._bootstrap).total_seconds() / 60
        active_visitors = 110 + 28 * sin(elapsed_minutes / 3)
        conversion_rate = 2.4 + 0.6 * sin(elapsed_minutes / 5)
        bounce_rate = 36 + 4 * cos(elapsed_minutes / 4)
        average_session = 3.8 + 0.4 * cos(elapsed_minutes / 6)

        return [
            RealtimeMetric(
                name="Aktive Besucher",
                value=max(45.0, active_visitors),
                unit="Besucher",
                trend_percentage=1.8 * cos(elapsed_minutes / 3),
            ),
            RealtimeMetric(
                name="Conversion-Rate",
                value=max(0.4, conversion_rate),
                unit="%",
                trend_percentage=1.2 * cos(elapsed_minutes / 5),
            ),
            RealtimeMetric(
                name="Absprungrate",
                value=max(10.0, bounce_rate),
                unit="%",
                trend_percentage=-1.5 * sin(elapsed_minutes / 4),
            ),
            RealtimeMetric(
                name="Ø Sitzungsdauer",
                value=max(1.2, average_session),
                unit="Minuten",
                trend_percentage=0.9 * cos(elapsed_minutes / 6),
            ),
        ]

    def web_sessions_timeseries(self, minutes: int = 60, interval: int = 5) -> list[TimeSeriesPoint]:
        """Return a rolling time series for active sessions."""

        if minutes <= 0 or interval <= 0:
            return []
        now = datetime.utcnow()
        points: list[TimeSeriesPoint] = []
        for minutes_ago in range(minutes, -1, -interval):
            timestamp = now - timedelta(minutes=minutes_ago)
            angle = (timestamp.minute + timestamp.second / 60) / 6
            value = 120 + 32 * sin(angle) + 12 * cos(angle / 2)
            points.append(TimeSeriesPoint(timestamp=timestamp, value=max(30.0, value)))
        return points

    def seo_health_score(self) -> float:
        """Return a synthetic SEO health score for the owned website."""

        elapsed_hours = (datetime.utcnow() - self._bootstrap).total_seconds() / 3600
        return 78 + 4.5 * sin(elapsed_hours / 2)


__all__ = [
    "KPI",
    "TimeSeriesPoint",
    "RealtimeMetric",
    "AnalyticsService",
]

