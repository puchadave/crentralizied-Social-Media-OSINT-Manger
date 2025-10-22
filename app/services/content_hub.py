from __future__ import annotations

from datetime import datetime
from typing import List

from sqlmodel import Session, select

from ..models import ContentItem, ContentItemCreate


class ContentHub:
    """Centralised content repository with AI-assisted creation."""

    def __init__(self, session: Session):
        self.session = session

    def list_items(self) -> List[ContentItem]:
        return self.session.exec(select(ContentItem)).all()

    def create_item(self, payload: ContentItemCreate) -> ContentItem:
        item = ContentItem.from_orm(payload)
        now = datetime.utcnow()
        item.created_at = now
        item.updated_at = now
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update_status(self, item_id: int, status: str) -> ContentItem:
        item = self.session.get(ContentItem, item_id)
        if not item:
            raise ValueError("Content item not found")
        item.status = status
        item.updated_at = datetime.utcnow()
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item


def generate_ai_caption(topic: str, tone: str = "professionell") -> str:
    """Return a deterministic AI-like caption to avoid external dependencies."""

    return (
        f"{topic.title()} — {tone} Insights: "
        "Jetzt handeln, Zielgruppe inspirieren und messbare Ergebnisse erzielen."
    )
