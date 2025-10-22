from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel


class ClientBase(SQLModel):
    name: str = Field(description="Name des Kunden oder Unternehmens.")
    industry: Optional[str] = Field(
        default=None, description="Branche oder vertikale Zuordnung des Kunden."
    )
    contact_email: str = Field(description="Primäre Kontaktadresse für das Account-Team.")
    phone: Optional[str] = Field(default=None, description="Telefonnummer für Rückfragen.")
    account_manager: Optional[str] = Field(
        default=None, description="Interner Ansprechpartner für den Kunden."
    )
    timezone: str = Field(default="Europe/Berlin", description="Zeitzone der Kundenorganisation.")
    billing_rate_per_minute: float = Field(
        default=2.4,
        description="Standard Cloud-/Service-Preis pro Minute für Kalkulationen.",
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict, description="Konfiguration & Automatisierungspräferenzen.", sa_column=Column(JSON)
    )


class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Aktivierungsstatus für Workflows.")


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: int
    created_at: datetime
    is_active: bool


class SiteBase(SQLModel):
    client_id: int = Field(foreign_key="client.id")
    name: str = Field(description="Name oder Zweck der Webpräsenz.")
    url: str = Field(description="Basis-URL der verwalteten Seite.")
    platform: str = Field(
        description="Zugehöriges CMS oder Technologie-Stack (WordPress, Ghost, Odoo, Custom)."
    )
    workspace: Optional[str] = Field(
        default=None, description="Optionaler Mandanten-/Workspace-Name für Multi-Tenancy."
    )
    api_connected: bool = Field(
        default=False, description="Gibt an, ob eine API-Integration aktiv verbunden ist."
    )
    connected_integrations: List[str] = Field(
        default_factory=list,
        description="Aktivierte Integrationen wie Analytics, Ads, Search Console.",
        sa_column=Column(JSON),
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Zusätzliche Konfigurationsparameter.", sa_column=Column(JSON)
    )
    last_synced_at: Optional[datetime] = Field(
        default=None, description="Letzte erfolgreiche Synchronisierung über APIs."
    )


class Site(SiteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


class SiteCreate(SiteBase):
    pass


class SiteRead(SiteBase):
    id: int
    created_at: datetime
    is_active: bool


class BudgetBase(SQLModel):
    client_id: int = Field(foreign_key="client.id")
    site_id: Optional[int] = Field(default=None, foreign_key="site.id")
    campaign_name: str = Field(description="Interne Referenz der Kampagne oder des Budgets.")
    channel: str = Field(description="Marketing-Kanal, z.B. google_ads, meta_ads, seo.")
    currency: str = Field(default="EUR", description="Währung der Budgetplanung.")
    allocated_budget: float = Field(description="Zugeteilter Betrag für den Zeitraum.")
    spent_budget: float = Field(default=0.0, description="Bisher verbrauchter Betrag.")
    period_start: datetime = Field(description="Startzeitraum des Budgets.")
    period_end: datetime = Field(description="Ende des Budgetzeitraums.")
    status: str = Field(
        default="active",
        description="Status wie active, paused, completed für Budgetsteuerung.",
    )
    kpi_target: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Zielwerte wie CPL, ROAS, Leads für Monitoring.",
        sa_column=Column(JSON),
    )


class BudgetAllocation(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BudgetCreate(BudgetBase):
    pass


class BudgetRead(BudgetBase):
    id: int
    created_at: datetime


class InvoiceBase(SQLModel):
    client_id: int = Field(foreign_key="client.id")
    reference: str = Field(description="Eindeutige Rechnungsnummer oder Referenz.")
    currency: str = Field(default="EUR")
    amount_due: float = Field(description="Gesamtbetrag der Rechnung.")
    status: str = Field(
        default="draft", description="Status wie draft, sent, paid, overdue."
    )
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    due_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=14),
        description="Fälligkeitsdatum der Rechnung.",
    )
    line_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Aufgeschlüsselte Positionen der Rechnung.",
        sa_column=Column(JSON),
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Invoice(InvoiceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceRead(InvoiceBase):
    id: int


class ProposalBase(SQLModel):
    client_id: int = Field(foreign_key="client.id")
    title: str = Field(description="Titel oder Angebotsname.")
    summary: str = Field(description="Kurzbeschreibung der angebotenen Leistungen.")
    currency: str = Field(default="EUR")
    line_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Berechnete Positionen inklusive Minutenpreise.",
        sa_column=Column(JSON),
    )
    estimated_minutes: float = Field(
        default=0.0, description="Gesamte kalkulierte Minuten für die Leistungen."
    )
    margin_percent: float = Field(
        default=0.2, description="Kalkulierte Gewinnmarge in Dezimalform."
    )
    total_value: float = Field(description="Gesamtangebot inklusive Marge.")
    status: str = Field(
        default="draft", description="Status wie draft, sent, accepted, rejected."
    )
    valid_until: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=30),
        description="Gültigkeitszeitraum des Angebots.",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Proposal(ProposalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProposalCreate(ProposalBase):
    pass


class ProposalRead(ProposalBase):
    id: int
    created_at: datetime


class PricingComponent(BaseModel):
    name: str
    minutes: float
    rate_per_minute: Optional[float] = PydanticField(
        default=None,
        description="Optionaler Override für den Minutenpreis."
    )
    category: Optional[str] = None
    notes: Optional[str] = None


class ProposalGenerationRequest(BaseModel):
    client_id: int
    title: str
    summary: Optional[str] = None
    components: List[PricingComponent]
    currency: str = "EUR"
    margin_percent: float = 0.2
    valid_days: int = 30
    include_subscription: bool = True


class ClientSummary(BaseModel):
    client: ClientRead
    total_sites: int
    active_budgets: int
    allocated_budget: float
    spent_budget: float
    outstanding_invoices: float
    proposals_in_progress: int
    monthly_recurring_revenue: float
    budgets: List[BudgetRead]
    invoices: List[InvoiceRead]
    proposals: List[ProposalRead]
    sites: List[SiteRead]

