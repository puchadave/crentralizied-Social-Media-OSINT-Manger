from __future__ import annotations

import asyncio
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select

from ..database import get_session
from ..models import OSINTEvent, OSINTEventCreate, OSINTEventRead
from ..services import nlp, osint_stream

router = APIRouter(prefix="/osint", tags=["osint"])


@router.post("/events", response_model=OSINTEventRead)
async def ingest_event(
    payload: OSINTEventCreate,
    session: Session = Depends(get_session),
) -> OSINTEvent:
    normalised_text = nlp.normalise_text(payload.text)
    sentiment = nlp.sentiment_score(normalised_text)
    tags = nlp.extract_tags(normalised_text)
    event = OSINTEvent(
        **payload.dict(exclude={"text", "sentiment", "tags"}),
        text=normalised_text,
        sentiment=sentiment,
        tags=tags,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    await osint_stream.publish(event)
    return event


@router.get("/events", response_model=List[OSINTEventRead])
async def list_events(session: Session = Depends(get_session)) -> List[OSINTEvent]:
    return session.exec(select(OSINTEvent).order_by(OSINTEvent.captured_at.desc()).limit(200)).all()


@router.websocket("/stream")
async def stream_events(websocket: WebSocket) -> None:
    await websocket.accept()
    async with osint_stream.register() as queue:
        try:
            while True:
                event = await queue.get()
                await websocket.send_json(jsonable_encoder(event))
        except WebSocketDisconnect:
            await websocket.close()
        except asyncio.CancelledError:  # pragma: no cover
            await websocket.close()
            raise
