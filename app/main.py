from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from .config import settings
from .database import init_db, session_scope
from .models import ContentItem, OSINTEvent, OSINTEventCreate
from .routers import analytics, automation, content, osint, seo
from .services import nlp, osint_stream


def create_application() -> FastAPI:
    app = FastAPI(title="Realtime Social Media Marketing OSINT Manager", version="0.1.0")
    app.include_router(osint.router)
    app.include_router(seo.router)
    app.include_router(content.router)
    app.include_router(automation.router)
    app.include_router(analytics.router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        init_db()
        if settings.enable_demo_data:
            await seed_demo_data()
            await stream_demo_events()

    return app


async def seed_demo_data() -> None:
    topics = [
        ("linkedin", "b2b leadgen strategie", "Starke Ergebnisse im SaaS-Markt"),
        ("twitter", "ki marketing", "Automatisierte Kampagnen in Echtzeit"),
        ("instagram", "branding", "Visuelles Storytelling mit KI"),
    ]
    with session_scope() as session:
        existing = session.exec(select(OSINTEvent).limit(1)).first()
        if existing:
            return
        for channel, tag, body in topics:
            item = ContentItem(
                channel=channel,
                title=f"{tag.title()} Launch",
                body=body,
                language="de",
                tags=[tag],
                status="published",
            )
            session.add(item)
        session.commit()


async def stream_demo_events() -> None:
    now = datetime.utcnow()
    demo_events: Iterable[OSINTEventCreate] = [
        OSINTEventCreate(
            platform="twitter",
            content_id="tw-1",
            author="growth_guru",
            text="Echtzeit-KI Monitoring ist fantastisch für B2B Leads!",
            language="de",
            engagement_score=0.8,
            tags=["b2b", "ki"],
            captured_at=now,
            event_at=now - timedelta(minutes=5),
        ),
        OSINTEventCreate(
            platform="linkedin",
            content_id="li-2",
            author="marketingmax",
            text="Automation reduziert unsere Kampagnenkosten stark.",
            language="de",
            engagement_score=0.9,
            tags=["automation"],
            captured_at=now,
            event_at=now - timedelta(minutes=15),
        ),
    ]
    with session_scope() as session:
        for payload in demo_events:
            normalised_text = nlp.normalise_text(payload.text)
            event = OSINTEvent(
                **payload.dict(exclude={"text"}),
                text=normalised_text,
                sentiment=nlp.sentiment_score(normalised_text),
                tags=nlp.extract_tags(normalised_text),
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            await osint_stream.publish(event)


app = create_application()
