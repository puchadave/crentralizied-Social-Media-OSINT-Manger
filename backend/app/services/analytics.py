"""Lightweight analytics helpers for OSINT data."""
from __future__ import annotations

from collections import Counter
from typing import Iterable

from ..models.monitoring import Interaction


def count_interaction_types(interactions: Iterable[Interaction]) -> Counter:
    """Return a counter grouped by interaction type."""

    counter: Counter = Counter()
    for interaction in interactions:
        counter[interaction.interaction_type] += 1
    return counter


def estimate_reach(interactions: Iterable[Interaction]) -> int:
    """Very rough reach estimation based on unique users and follower counts."""

    reach = 0
    seen_users: set[str] = set()
    for interaction in interactions:
        if interaction.user_id in seen_users:
            continue
        seen_users.add(interaction.user_id)
        followers = interaction.follower_count or 0
        reach += 1 + int(followers * 0.1)
    return reach
