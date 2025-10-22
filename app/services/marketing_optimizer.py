from __future__ import annotations

from datetime import datetime, timedelta
from statistics import mean
from typing import Dict, List

from sqlmodel import Session, select

from ..config import settings
from ..models import ContentItem, OSINTEvent


class MarketingOptimizer:
    """Generate realtime marketing insights from OSINT events and content library."""

    def __init__(self, session: Session):
        self.session = session

    def best_posting_times(self, platform: str) -> Dict[str, float]:
        cutoff = datetime.utcnow() - timedelta(hours=settings.marketing_lookback_hours)
        events = self.session.exec(
            select(OSINTEvent).where(
                OSINTEvent.platform == platform,
                OSINTEvent.captured_at >= cutoff,
            )
        ).all()
        if not events:
            return {"08:00": 0.5, "12:00": 0.5}
        buckets: Dict[str, List[float]] = {}
        for event in events:
            slot = event.event_at.strftime("%H:00")
            buckets.setdefault(slot, []).append(event.engagement_score)
        return {slot: mean(scores) for slot, scores in buckets.items()}

    def campaign_health(self) -> Dict[str, float]:
        contents = self.session.exec(select(ContentItem)).all()
        platforms: Dict[str, List[float]] = {}
        for item in contents:
            platforms.setdefault(item.channel, []).append(1.0 if item.status == "published" else 0.3)
        return {platform: mean(scores) for platform, scores in platforms.items()}
