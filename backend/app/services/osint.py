"""OSINT ingestion and analytics service layer."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..models.monitoring import (
    Interaction,
    InteractionIngestRequest,
    InteractionSummary,
    NetworkEdge,
    NetworkGraph,
    NetworkNode,
)
from .analytics import count_interaction_types, estimate_reach


@dataclass
class _PostInteractions:
    platform: str
    interactions: List[Interaction]


class OsintService:
    """Store monitored interactions and derive insights from them."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._posts: Dict[str, _PostInteractions] = {}

    def ingest(self, request: InteractionIngestRequest) -> InteractionSummary:
        """Persist interactions for a monitored post and return updated summary."""

        with self._lock:
            post = self._posts.get(request.post_id)
            if not post:
                post = _PostInteractions(platform=request.platform, interactions=[])
                self._posts[request.post_id] = post
            else:
                post.platform = request.platform

            post.interactions.extend(request.interactions)
            return self._build_summary_locked(request.post_id, post)

    def get_summary(self, post_id: str) -> Optional[InteractionSummary]:
        """Return an aggregated summary for a post if data is available."""

        with self._lock:
            post = self._posts.get(post_id)
            if not post:
                return None
            return self._build_summary_locked(post_id, post)

    def get_network_graph(self, post_id: str) -> Optional[NetworkGraph]:
        """Return a simple network graph for the requested post."""

        with self._lock:
            post = self._posts.get(post_id)
            if not post:
                return None

            nodes: Dict[str, NetworkNode] = {
                post_id: NetworkNode(id=post_id, label=f"Post {post_id}", type="post")
            }
            edges: list[NetworkEdge] = []

            for interaction in post.interactions:
                user_node = nodes.get(interaction.user_id)
                if not user_node:
                    label = interaction.user_display_name or interaction.user_id
                    user_node = NetworkNode(id=interaction.user_id, label=label, type="user")
                    nodes[interaction.user_id] = user_node
                edges.append(NetworkEdge(source=interaction.user_id, target=post_id, weight=1))

                if interaction.in_reply_to:
                    reply_node = nodes.get(interaction.in_reply_to)
                    if not reply_node:
                        reply_node = NetworkNode(
                            id=interaction.in_reply_to,
                            label=interaction.in_reply_to,
                            type="user",
                        )
                        nodes[interaction.in_reply_to] = reply_node
                    edges.append(NetworkEdge(source=interaction.user_id, target=interaction.in_reply_to, weight=1))

            return NetworkGraph(nodes=list(nodes.values()), edges=edges)

    def list_post_ids(self) -> list[str]:
        """Return the IDs of all monitored posts."""

        with self._lock:
            return list(self._posts.keys())

    def _build_summary_locked(
        self, post_id: str, interactions: _PostInteractions
    ) -> InteractionSummary:
        """Build an :class:`InteractionSummary` for the provided interactions."""

        counter = count_interaction_types(interactions.interactions)
        unique_users = len({entry.user_id for entry in interactions.interactions})
        reach = estimate_reach(interactions.interactions)
        return InteractionSummary(
            post_id=post_id,
            platform=interactions.platform,
            total_interactions=len(interactions.interactions),
            unique_users=unique_users,
            comments=counter.get("comment", 0),
            reposts=counter.get("repost", 0),
            likes=counter.get("like", 0),
            estimated_reach=reach,
        )
