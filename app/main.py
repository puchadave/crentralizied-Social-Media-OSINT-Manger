from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from .config import settings
from .database import init_db, session_scope
from .frontend import router as frontend_router
from .models import (
    BudgetAllocation,
    Client,
    ContentItem,
    Invoice,
    OSINTEvent,
    OSINTEventCreate,
    Proposal,
    SearchMetric,
    Site,
    WebMetric,
)
from .routers import analytics, automation, billing, clients, content, osint, seo
from .services import nlp, osint_stream


def create_application() -> FastAPI:
    app = FastAPI(title="Realtime Social Media Marketing OSINT Manager", version="0.1.0")
    app.include_router(frontend_router)
    app.include_router(osint.router)
    app.include_router(seo.router)
    app.include_router(content.router)
    app.include_router(automation.router)
    app.include_router(analytics.router)
    app.include_router(clients.router)
    app.include_router(billing.router)

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

        window_end = datetime.utcnow()
        window_start = window_end - timedelta(hours=1)
        for source, metric, value in [
            ("website", "sessions", 1860.0),
            ("website", "pageviews", 4320.0),
            ("website", "conversions", 148.0),
            ("website", "bounce_rate", 36.0),
            ("website", "session_duration_seconds", 212.0),
            ("landingpage", "sessions", 640.0),
        ]:
            session.add(
                WebMetric(
                    source=source,
                    metric=metric,
                    value=value,
                    period_start=window_start,
                    period_end=window_end,
                    metadata={"seed": "demo"},
                )
            )

        search_window_start = window_end - timedelta(days=1)
        for query, clicks, impressions, ctr, position in [
            ("osint marketing", 320.0, 6400.0, 5.0, 3.2),
            ("realtime seo", 210.0, 3900.0, 5.4, 4.1),
            ("automation dashboard", 140.0, 2600.0, 5.3, 5.0),
        ]:
            session.add(
                SearchMetric(
                    query=query,
                    clicks=clicks,
                    impressions=impressions,
                    ctr=ctr,
                    position=position,
                    period_start=search_window_start,
                    period_end=window_end,
                    metadata={"seed": "demo"},
                )
            )

        # Demo Kunden & Mandantenverwaltung
        digital_growth = Client(
            name="Digital Growth GmbH",
            industry="SaaS",
            contact_email="ops@digitalgrowth.example",
            account_manager="Lena Analytics",
            timezone="Europe/Berlin",
            billing_rate_per_minute=2.8,
            preferences={
                "reporting_language": "de",
                "preferred_channels": ["google_ads", "linkedin"],
            },
        )
        session.add(digital_growth)
        session.commit()
        session.refresh(digital_growth)

        ecom_sprint = Client(
            name="Ecom Sprint AG",
            industry="E-Commerce",
            contact_email="commerce@ecomsprint.example",
            account_manager="Mia Performance",
            timezone="Europe/Berlin",
            billing_rate_per_minute=2.1,
            preferences={"reporting_language": "en", "preferred_channels": ["meta_ads"]},
        )
        session.add(ecom_sprint)
        session.commit()
        session.refresh(ecom_sprint)

        digital_sites = [
            Site(
                client_id=digital_growth.id,
                name="Corporate",
                url="https://digitalgrowth.example",
                platform="wordpress",
                workspace="digitalgrowth",
                api_connected=True,
                connected_integrations=["analytics", "search_console", "google_ads"],
                metadata={"audience": "b2b", "language": "de"},
                last_synced_at=window_end,
            ),
            Site(
                client_id=digital_growth.id,
                name="Product Hub",
                url="https://hub.digitalgrowth.example",
                platform="ghost",
                workspace="dg-products",
                api_connected=True,
                connected_integrations=["analytics", "seo", "automation"],
                metadata={"audience": "product-led", "language": "en"},
                last_synced_at=window_end,
            ),
        ]
        for site in digital_sites:
            session.add(site)
        session.commit()
        for site in digital_sites:
            session.refresh(site)

        ecom_site = Site(
            client_id=ecom_sprint.id,
            name="Storefront",
            url="https://shop.ecomsprint.example",
            platform="odoo",
            workspace="ecom-shop",
            api_connected=True,
            connected_integrations=["analytics", "google_ads", "meta_ads"],
            metadata={"audience": "d2c", "language": "de"},
            last_synced_at=window_end,
        )
        session.add(ecom_site)
        session.commit()
        session.refresh(ecom_site)

        # Budget- und Abrechnungssimulation
        budgets = [
            BudgetAllocation(
                client_id=digital_growth.id,
                site_id=digital_sites[0].id,
                campaign_name="Brand Awareness Q1",
                channel="google_ads",
                currency="EUR",
                allocated_budget=12000.0,
                spent_budget=3400.0,
                period_start=window_end - timedelta(days=15),
                period_end=window_end + timedelta(days=15),
                status="active",
                kpi_target={"cpl": 45.0, "roas": 4.5},
            ),
            BudgetAllocation(
                client_id=digital_growth.id,
                site_id=digital_sites[1].id,
                campaign_name="Product-Led SEO",
                channel="seo",
                currency="EUR",
                allocated_budget=4800.0,
                spent_budget=1600.0,
                period_start=window_end - timedelta(days=30),
                period_end=window_end + timedelta(days=30),
                status="active",
                kpi_target={"organic_sessions": 5000, "sqls": 120},
            ),
            BudgetAllocation(
                client_id=ecom_sprint.id,
                site_id=ecom_site.id,
                campaign_name="Performance Max",
                channel="google_ads",
                currency="EUR",
                allocated_budget=18000.0,
                spent_budget=9600.0,
                period_start=window_end - timedelta(days=10),
                period_end=window_end + timedelta(days=20),
                status="active",
                kpi_target={"roas": 6.0, "orders": 420},
            ),
        ]
        for budget in budgets:
            session.add(budget)

        invoices = [
            Invoice(
                client_id=digital_growth.id,
                reference="DG-2024-001",
                amount_due=8200.0,
                status="sent",
                line_items=[
                    {"description": "Google Ads Media Spend", "amount": 5000.0},
                    {"description": "KI-Automation & Reporting", "amount": 1800.0},
                    {"description": "CMS Optimierung", "amount": 1400.0},
                ],
                metadata={"period": "2024-02"},
            ),
            Invoice(
                client_id=digital_growth.id,
                reference="DG-2024-002",
                amount_due=6400.0,
                status="paid",
                line_items=[
                    {"description": "LinkedIn Kampagnen", "amount": 3600.0},
                    {"description": "Realtime Dashboard Lizenz", "amount": 2800.0},
                ],
                metadata={"period": "2024-01"},
            ),
            Invoice(
                client_id=ecom_sprint.id,
                reference="EC-2024-001",
                amount_due=5400.0,
                status="sent",
                line_items=[
                    {"description": "Performance Max Betreuung", "amount": 4200.0},
                    {"description": "SEO Content Automation", "amount": 1200.0},
                ],
                metadata={"period": "2024-02"},
            ),
        ]
        for invoice in invoices:
            session.add(invoice)

        proposals = [
            Proposal(
                client_id=digital_growth.id,
                title="Realtime Growth Paket Q2",
                summary="Always-on OSINT, Ads Budgetsteuerung und SEO Sprints.",
                currency="EUR",
                line_items=[
                    {
                        "name": "Strategic Growth Sprint",
                        "minutes": 960.0,
                        "rate_per_minute": 2.8,
                        "category": "service",
                        "cost": 2688.0,
                    },
                    {
                        "name": "Cloud Automation & Monitoring",
                        "minutes": 240.0,
                        "rate_per_minute": 2.8,
                        "category": "subscription",
                        "cost": 672.0,
                    },
                ],
                estimated_minutes=1200.0,
                margin_percent=0.25,
                total_value=4190.0,
                status="sent",
                metadata={"generated": False, "region": "DACH"},
            ),
            Proposal(
                client_id=ecom_sprint.id,
                title="E-Com Skalierung",
                summary="Automatisierte Ads & SEO Optimierung für D2C Retail.",
                currency="EUR",
                line_items=[
                    {
                        "name": "Performance Ads Automation",
                        "minutes": 720.0,
                        "rate_per_minute": 2.1,
                        "category": "service",
                        "cost": 1512.0,
                    },
                    {
                        "name": "Realtime KPI Dashboard",
                        "minutes": 180.0,
                        "rate_per_minute": 2.1,
                        "category": "subscription",
                        "cost": 378.0,
                    },
                ],
                estimated_minutes=900.0,
                margin_percent=0.2,
                total_value=2268.0,
                status="draft",
                metadata={"generated": False, "region": "EU"},
            ),
        ]
        for proposal in proposals:
            session.add(proposal)

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
                **payload.dict(exclude={"text", "sentiment", "tags"}),
                text=normalised_text,
                sentiment=nlp.sentiment_score(normalised_text),
                tags=nlp.extract_tags(normalised_text),
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            await osint_stream.publish(event)


app = create_application()
