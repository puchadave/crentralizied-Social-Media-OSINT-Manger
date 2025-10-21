"""Simple in-memory scheduling utilities for generated posts."""
from __future__ import annotations

import threading
import uuid
from typing import Dict

from ..models.scheduling import SchedulePostRequest, ScheduledPost, ScheduledPostCollection
from ..utils.time import utc_now


class SchedulerService:
    """Maintain scheduled posts and provide simple CRUD helpers."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._posts: Dict[str, ScheduledPost] = {}

    def schedule_post(self, request: SchedulePostRequest) -> ScheduledPost:
        """Persist a scheduled post entry."""

        with self._lock:
            post_id = uuid.uuid4().hex
            now = utc_now()
            scheduled = ScheduledPost(
                id=post_id,
                status="scheduled",
                created_at=now,
                updated_at=now,
                content=request.content,
                scheduled_time=request.scheduled_time,
                platforms=request.platforms,
                campaign=request.campaign,
            )
            self._posts[post_id] = scheduled
            return scheduled

    def list_posts(self) -> ScheduledPostCollection:
        """Return all scheduled posts sorted by schedule timestamp."""

        with self._lock:
            items = sorted(self._posts.values(), key=lambda post: post.scheduled_time)
            return ScheduledPostCollection(items=list(items))

    def get_post(self, post_id: str) -> ScheduledPost | None:
        """Return a scheduled post by id if available."""

        with self._lock:
            return self._posts.get(post_id)

    def update_status(self, post_id: str, status: str) -> ScheduledPost | None:
        """Update the status of a scheduled post."""

        with self._lock:
            post = self._posts.get(post_id)
            if not post:
                return None
            updated = post.copy(update={"status": status, "updated_at": utc_now()})
            self._posts[post_id] = updated
            return updated
