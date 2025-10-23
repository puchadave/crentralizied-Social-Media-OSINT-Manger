from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

from sqlmodel import Session, select

from ..models import OSINTEvent, SearchMetric, WebMetric
from .marketing_optimizer import MarketingOptimizer
from .visualization import mention_volume, sentiment_over_time


def _latest_metric(session: Session, metric: str) -> float:
    statement = (
        select(WebMetric)
        .where(WebMetric.metric == metric)
        .order_by(WebMetric.period_end.desc())
        .limit(1)
    )
    result = session.exec(statement).first()
    return result.value if result else 0.0


def kpi_overview(session: Session) -> Dict[str, float]:
    """Return zentrale KPIs ähnlich Google Analytics."""

    return {
        "sessions": _latest_metric(session, "sessions"),
        "pageviews": _latest_metric(session, "pageviews"),
        "conversions": _latest_metric(session, "conversions"),
        "avg_session_duration": _latest_metric(session, "session_duration_seconds"),
        "bounce_rate": _latest_metric(session, "bounce_rate"),
    }


def traffic_breakdown(session: Session) -> Dict[str, float]:
    metrics = session.exec(select(WebMetric)).all()
    breakdown: Dict[str, float] = defaultdict(float)
    for metric in metrics:
        if metric.metric == "sessions":
            breakdown[metric.source] += metric.value
    return dict(breakdown)


def search_console_snapshot(session: Session) -> Dict[str, Dict[str, float]]:
    metrics = session.exec(select(SearchMetric).order_by(SearchMetric.period_end.desc())).all()
    snapshot: Dict[str, Dict[str, float]] = {}
    for metric in metrics:
        if metric.query in snapshot:
            continue
        snapshot[metric.query] = {
            "clicks": metric.clicks,
            "impressions": metric.impressions,
            "ctr": metric.ctr,
            "position": metric.position,
        }
    return snapshot


def realtime_engagement(session: Session) -> Dict[str, float]:
    window = datetime.utcnow() - timedelta(hours=24)
    events = session.exec(
        select(OSINTEvent).where(OSINTEvent.event_at >= window).order_by(OSINTEvent.event_at)
    ).all()
    if not events:
        return {"events": 0, "avg_sentiment": 0.0, "engagement_score": 0.0}
    avg_sentiment = sum(event.sentiment for event in events) / len(events)
    avg_engagement = sum(event.engagement_score for event in events) / len(events)
    return {
        "events": float(len(events)),
        "avg_sentiment": avg_sentiment,
        "engagement_score": avg_engagement,
    }


def dashboard_overview(session: Session) -> Dict[str, Dict[str, float]]:
    marketing = MarketingOptimizer(session)
    sentiment_snapshot: Dict[str, float] = {}
    volumes = mention_volume(session)
    for platform in volumes.keys():
        series = sentiment_over_time(session, platform)["series"]
        sentiment_snapshot[platform] = series[-1]["sentiment"] if series else 0.0
    return {
        "osint": {"volume": volumes, "sentiment": sentiment_snapshot},
        "kpis": kpi_overview(session),
        "traffic": traffic_breakdown(session),
        "search_console": search_console_snapshot(session),
        "marketing": marketing.campaign_health(),
        "engagement": realtime_engagement(session),
    }
