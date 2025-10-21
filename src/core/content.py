"""Content management logic for the centralized OSINT marketing platform."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Sequence
import json
import uuid


@dataclass(slots=True)
class ContentItem:
    """Represents a single marketing content asset."""

    id: str
    title: str
    body: str
    networks: List[str]
    created_at: datetime
    scheduled_for: datetime | None = None
    tags: List[str] = field(default_factory=list)
    media_path: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "ContentItem":
        created_at = datetime.fromisoformat(data["created_at"])
        scheduled_raw = data.get("scheduled_for")
        scheduled_for = datetime.fromisoformat(scheduled_raw) if scheduled_raw else None
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data["title"],
            body=data["body"],
            networks=list(data.get("networks", [])),
            created_at=created_at,
            scheduled_for=scheduled_for,
            tags=list(data.get("tags", [])),
            media_path=data.get("media_path"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "networks": list(self.networks),
            "created_at": self.created_at.isoformat(),
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "tags": list(self.tags),
            "media_path": self.media_path,
        }


class ContentRepository:
    """Persists and serves :class:`ContentItem` instances."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._items: list[ContentItem] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            self._items = []
            return
        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self._items = [ContentItem.from_dict(item) for item in raw]

    def _persist(self) -> None:
        serialisable = [item.to_dict() for item in self._items]
        self.storage_path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")

    def all(self) -> Sequence[ContentItem]:
        return tuple(self._items)

    def add_content(
        self,
        title: str,
        body: str,
        networks: Iterable[str],
        *,
        scheduled_for: datetime | None = None,
        tags: Iterable[str] | None = None,
        media_path: str | None = None,
    ) -> ContentItem:
        item = ContentItem(
            id=str(uuid.uuid4()),
            title=title,
            body=body,
            networks=list(networks),
            created_at=datetime.utcnow(),
            scheduled_for=scheduled_for,
            tags=list(tags or []),
            media_path=media_path,
        )
        self._items.append(item)
        self._persist()
        return item

    def search(self, keyword: str) -> list[ContentItem]:
        keyword_lower = keyword.lower()
        return [
            item
            for item in self._items
            if keyword_lower in item.title.lower() or keyword_lower in item.body.lower()
        ]

    def by_network(self, network: str) -> list[ContentItem]:
        network_lower = network.lower()
        return [item for item in self._items if network_lower in (n.lower() for n in item.networks)]

    def seed_from(self, path: Path) -> None:
        if self._items or not path.exists():
            return
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._items = [ContentItem.from_dict(item) for item in raw]
        self._persist()

