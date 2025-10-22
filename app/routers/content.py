from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import ContentItem, ContentItemCreate, ContentItemRead
from ..services.content_hub import ContentHub, generate_ai_caption

router = APIRouter(prefix="/content", tags=["content"])


def get_hub(session: Session = Depends(get_session)) -> ContentHub:
    return ContentHub(session)


@router.get("/", response_model=List[ContentItemRead])
async def list_content(hub: ContentHub = Depends(get_hub)) -> List[ContentItem]:
    return hub.list_items()


@router.post("/", response_model=ContentItemRead)
async def create_content(payload: ContentItemCreate, hub: ContentHub = Depends(get_hub)) -> ContentItem:
    return hub.create_item(payload)


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
