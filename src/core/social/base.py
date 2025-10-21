"""Abstractions for social media network integrations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(slots=True)
class SocialPost:
    id: str
    author: str
    content: str
    network: str
    created_at: str
    url: str
    replies: int = 0
    reactions: int = 0


@dataclass(slots=True)
class Comment:
    id: str
    post_id: str
    author: str
    content: str
    created_at: str


class SocialConnector(Protocol):
    """Interface that connectors must implement."""

    network: str

    def fetch_recent_posts(self) -> Iterable[SocialPost]:
        ...

    def fetch_comments(self, post_id: str) -> Iterable[Comment]:
        ...

    def publish(self, content: str, *, media_path: str | None = None) -> SocialPost:
        ...

