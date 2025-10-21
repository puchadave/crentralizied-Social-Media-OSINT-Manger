"""Routes for scheduling generated content."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ...dependencies import get_scheduler_service
from ...models.scheduling import (
    SchedulePostRequest,
    ScheduledPost,
    ScheduledPostCollection,
)
from ...services.scheduler import SchedulerService

router = APIRouter(prefix="/posts", tags=["scheduling"])


@router.post("/schedule", response_model=ScheduledPost, status_code=status.HTTP_201_CREATED)
def schedule_post(
    payload: SchedulePostRequest,
    service: SchedulerService = Depends(get_scheduler_service),
) -> ScheduledPost:
    """Schedule a newly generated post for publishing."""

    return service.schedule_post(payload)


@router.get("/schedule", response_model=ScheduledPostCollection)
def list_scheduled_posts(
    service: SchedulerService = Depends(get_scheduler_service),
) -> ScheduledPostCollection:
    """Return all currently scheduled posts."""

    return service.list_posts()


@router.get("/{post_id}", response_model=ScheduledPost)
def get_scheduled_post(
    post_id: str,
    service: SchedulerService = Depends(get_scheduler_service),
) -> ScheduledPost:
    """Retrieve a single scheduled post by its identifier."""

    post = service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post
