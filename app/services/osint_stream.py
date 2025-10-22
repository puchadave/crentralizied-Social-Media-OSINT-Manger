from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncIterator, Dict, Iterable, List

from sqlmodel import Session, select

from ..database import session_scope
from ..models import OSINTEvent, OSINTSummary
from . import nlp


class OSINTStream:
    """Manage realtime OSINT events, analytics aggregation and subscriptions."""

    def __init__(self) -> None:
        self._subscribers: List[asyncio.Queue[OSINTEvent]] = []
        self._lock = asyncio.Lock()

    async def publish(self, event: OSINTEvent) -> None:
        async with self._lock:
            for queue in list(self._subscribers):
                await queue.put(event)

    @asynccontextmanager
    async def register(self) -> AsyncIterator[asyncio.Queue[OSINTEvent]]:
        queue: asyncio.Queue[OSINTEvent] = asyncio.Queue(maxsize=1000)
        async with self._lock:
            self._subscribers.append(queue)
        try:
            yield queue
        finally:
            async with self._lock:
                if queue in self._subscribers:
                    self._subscribers.remove(queue)

    def aggregate(self, hours: int = 24) -> List[OSINTSummary]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with session_scope() as session:
            events = session.exec(
                select(OSINTEvent).where(OSINTEvent.captured_at >= cutoff)
            ).all()
            return list(self._build_summaries(events, session))

    def _build_summaries(
        self, events: Iterable[OSINTEvent], session: Session
    ) -> Iterable[OSINTSummary]:
        grouped: Dict[str, List[OSINTEvent]] = {}
        for event in events:
            grouped.setdefault(event.platform, []).append(event)
        summaries: List[OSINTSummary] = []
        for platform, platform_events in grouped.items():
            if not platform_events:
                continue
            mention_volume = len(platform_events)
            avg_sentiment = sum(e.sentiment for e in platform_events) / mention_volume
            top_tags = [tag for tag, _ in nlp.keyword_frequencies(e.text for e in platform_events)[:10]]
            summary = OSINTSummary(
                period_start=min(e.captured_at for e in platform_events),
                period_end=max(e.captured_at for e in platform_events),
                platform=platform,
                mention_volume=mention_volume,
                average_sentiment=avg_sentiment,
                top_tags=top_tags,
            )
            session.merge(summary)
            summaries.append(summary)
        session.commit()
        return summaries


osint_stream = OSINTStream()
