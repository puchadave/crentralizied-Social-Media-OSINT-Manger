"""In-memory placeholder connectors for the supported networks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from ..config import IntegrationSettings
from ..integrations import SOCIAL_NETWORK_DEFINITIONS
from .base import Comment, SocialConnector, SocialPost


@dataclass(slots=True)
class _StaticConnector(SocialConnector):
    network: str
    posts: List[SocialPost]

    def fetch_recent_posts(self) -> Iterable[SocialPost]:
        return list(self.posts)

    def fetch_comments(self, post_id: str) -> Iterable[Comment]:
        return [
            Comment(
                id=f"{post_id}-c{i}",
                post_id=post_id,
                author="Community Manager",
                content=f"Automated response {i} for {self.network}",
                created_at="2024-04-01T12:00:00Z",
            )
            for i in range(1, 3)
        ]

    def publish(self, content: str, *, media_path: str | None = None) -> SocialPost:
        post = SocialPost(
            id=f"{self.network.lower().replace(' ', '-')}-{len(self.posts) + 1}",
            author="Automation Bot",
            content=content,
            network=self.network,
            created_at="2024-04-01T09:00:00Z",
            url=f"https://{self.network.lower().replace(' ', '-')}.example.com/post/{len(self.posts) + 1}",
            replies=0,
            reactions=0,
        )
        self.posts.append(post)
        return post


def build_connectors(settings: IntegrationSettings | None = None) -> list[SocialConnector]:
    base_posts = [
        SocialPost(
            id="seed-1",
            author="Marketing Team",
            content="Welcome to the unified OSINT marketing cockpit!",
            network="Shared",
            created_at="2024-04-01T08:00:00Z",
            url="https://example.com/post/seed-1",
            replies=12,
            reactions=58,
        )
    ]
    connectors: list[SocialConnector] = []
    for definition in SOCIAL_NETWORK_DEFINITIONS:
        name = definition["name"]
        status = settings.status_for("social", name) if settings else "unconfigured"
        label = name if status == "connected" else f"{name} (offline)"
        connectors.append(_StaticConnector(network=label, posts=list(base_posts)))
    return connectors


__all__ = ["build_connectors"]
