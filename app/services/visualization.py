from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from sqlmodel import Session, select

from ..models import OSINTEvent


def sentiment_over_time(session: Session, platform: str) -> Dict[str, List[Dict[str, float]]]:
    events = session.exec(
        select(OSINTEvent).where(OSINTEvent.platform == platform).order_by(OSINTEvent.event_at)
    ).all()
    buckets: Dict[str, List[float]] = defaultdict(list)
    for event in events:
        key = event.event_at.strftime("%Y-%m-%d %H:00")
        buckets[key].append(event.sentiment)
    return {
        "platform": platform,
        "series": [
            {"timestamp": timestamp, "sentiment": sum(values) / len(values)}
            for timestamp, values in buckets.items()
        ],
    }


def mention_volume(session: Session) -> Dict[str, int]:
    events = session.exec(select(OSINTEvent.platform)).all()
    volume: Dict[str, int] = defaultdict(int)
    for (platform,) in events:
        volume[platform] += 1
    return dict(volume)
