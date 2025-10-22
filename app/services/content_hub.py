from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from sqlmodel import Session, select

from ..models import ContentItem, ContentItemCreate
from .social_connectors import SocialNetworkRouter


class ContentHub:
    """Centralised content repository with AI-assisted creation und Distribution."""

    def __init__(self, session: Session, router: SocialNetworkRouter | None = None):
        self.session = session
        self.router = router or SocialNetworkRouter()

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

    def available_destinations(self) -> Dict[str, List[str]]:
        return self.router.available()

    def dispatch_item(
        self, item_id: int, networks: Iterable[str]
    ) -> Tuple[ContentItem, Dict[str, Dict[str, str]]]:
        item = self.session.get(ContentItem, item_id)
        if not item:
            raise ValueError("Content item not found")
        statuses = self.router.publish(item, networks)
        if not statuses:
            raise ValueError("No supported networks requested")
        metadata = item.metadata or {}
        destinations: Dict[str, Dict[str, str]] = metadata.get("destinations", {})
        destinations.update(statuses)
        metadata["destinations"] = destinations
        metadata["last_dispatch"] = datetime.utcnow().isoformat()
        item.metadata = metadata
        item.status = "published"
        item.updated_at = datetime.utcnow()
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item, statuses


def generate_ai_caption(topic: str, tone: str = "professionell") -> str:
    """Return a deterministic AI-like caption to avoid external dependencies."""

    return (
        f"{topic.title()} — {tone} Insights: "
        "Jetzt handeln, Zielgruppe inspirieren und messbare Ergebnisse erzielen."
    )
