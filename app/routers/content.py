from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import (
    ContentDispatchResponse,
    ContentItem,
    ContentItemCreate,
    ContentItemRead,
)
from ..models.content import DispatchStatus
from ..services.content_hub import ContentHub, generate_ai_caption
from ..services.social_connectors import SocialNetworkRouter

router = APIRouter(prefix="/content", tags=["content"])


def get_hub(session: Session = Depends(get_session)) -> ContentHub:
    return ContentHub(session, router=SocialNetworkRouter())


@router.get("/", response_model=List[ContentItemRead])
async def list_content(hub: ContentHub = Depends(get_hub)) -> List[ContentItem]:
    return hub.list_items()


@router.post("/", response_model=ContentItemRead)
async def create_content(payload: ContentItemCreate, hub: ContentHub = Depends(get_hub)) -> ContentItem:
    return hub.create_item(payload)


@router.get("/destinations", response_model=Dict[str, List[str]])
async def available_destinations(hub: ContentHub = Depends(get_hub)) -> Dict[str, List[str]]:
    return hub.available_destinations()


@router.post("/generate", response_model=ContentItemRead)
async def generate_content(
    topic: str,
    tone: str = "professionell",
    channel: str = "linkedin",
    hub: ContentHub = Depends(get_hub),
) -> ContentItem:
    caption = generate_ai_caption(topic, tone=tone)
    payload = ContentItemCreate(
        channel=channel,
        title=f"{topic.title()} Kampagne",
        body=caption,
        language="de",
        tags=[topic.lower(), tone],
    )
    return hub.create_item(payload)


@router.post("/{item_id}/status", response_model=ContentItemRead)
async def update_status(item_id: int, status: str, hub: ContentHub = Depends(get_hub)) -> ContentItem:
    try:
        return hub.update_status(item_id, status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{item_id}/publish", response_model=ContentDispatchResponse)
async def publish_content(
    item_id: int,
    networks: List[str] = Body(..., embed=True, description="Zielnetzwerke"),
    hub: ContentHub = Depends(get_hub),
) -> ContentDispatchResponse:
    try:
        item, statuses = hub.dispatch_item(item_id, networks)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc
    return ContentDispatchResponse(
        item=ContentItemRead.from_orm(item),
        destinations={name: DispatchStatus(**status) for name, status in statuses.items()},
    )
