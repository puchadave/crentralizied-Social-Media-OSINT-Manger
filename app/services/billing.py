from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from sqlmodel import Session, select

from ..models import (
    BudgetAllocation,
    BudgetCreate,
    BudgetRead,
    Client,
    Invoice,
    InvoiceCreate,
    InvoiceRead,
    Proposal,
    ProposalCreate,
    ProposalGenerationRequest,
    ProposalRead,
)


class BillingEngine:
    """Zentrale Abrechnung über Budgets, Rechnungen und Angebote."""

    def __init__(self, session: Session):
        self.session = session

    # --- Budget Management -------------------------------------------------
    def list_budgets(self, client_id: Optional[int] = None) -> List[BudgetAllocation]:
        statement = select(BudgetAllocation)
        if client_id is not None:
            statement = statement.where(BudgetAllocation.client_id == client_id)
        statement = statement.order_by(BudgetAllocation.period_end.desc())
        return list(self.session.exec(statement).all())

    def create_budget(self, payload: BudgetCreate) -> BudgetAllocation:
        self._ensure_client(payload.client_id)
        budget = BudgetAllocation(**payload.dict())
        if budget.spent_budget > budget.allocated_budget:
            raise ValueError("Spent budget darf den zugeteilten Betrag nicht übersteigen")
        self.session.add(budget)
        self.session.commit()
        self.session.refresh(budget)
        return budget

    def record_spend(self, budget_id: int, delta: float) -> BudgetAllocation:
        budget = self.session.get(BudgetAllocation, budget_id)
        if not budget:
            raise ValueError("Budget nicht gefunden")
        new_value = max(0.0, budget.spent_budget + delta)
        budget.spent_budget = min(new_value, budget.allocated_budget)
        if budget.spent_budget >= budget.allocated_budget and budget.status == "active":
            budget.status = "completed"
        self.session.add(budget)
        self.session.commit()
        self.session.refresh(budget)
        return budget

    # --- Invoice Management ------------------------------------------------
    def list_invoices(self, client_id: Optional[int] = None) -> List[Invoice]:
        statement = select(Invoice)
        if client_id is not None:
            statement = statement.where(Invoice.client_id == client_id)
        statement = statement.order_by(Invoice.issued_at.desc())
        return list(self.session.exec(statement).all())

    def create_invoice(self, payload: InvoiceCreate) -> Invoice:
        self._ensure_client(payload.client_id)
        invoice = Invoice(**payload.dict())
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        return invoice

    def set_invoice_status(self, invoice_id: int, status: str) -> Invoice:
        invoice = self.session.get(Invoice, invoice_id)
        if not invoice:
            raise ValueError("Rechnung nicht gefunden")
        invoice.status = status
        if status == "paid":
            metadata = dict(invoice.metadata_ or {})
            metadata["paid_at"] = datetime.utcnow().isoformat()
            invoice.metadata_ = metadata
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        return invoice

    # --- Proposal Management -----------------------------------------------
    def list_proposals(self, client_id: Optional[int] = None) -> List[Proposal]:
        statement = select(Proposal)
        if client_id is not None:
            statement = statement.where(Proposal.client_id == client_id)
        statement = statement.order_by(Proposal.created_at.desc())
        return list(self.session.exec(statement).all())

    def generate_proposal(self, request: ProposalGenerationRequest) -> Proposal:
        client = self._ensure_client(request.client_id)
        base_rate = client.billing_rate_per_minute

        line_items = []
        total_minutes = 0.0
        for component in request.components:
            rate = component.rate_per_minute or base_rate
            cost = component.minutes * rate
            line_items.append(
                {
                    "name": component.name,
                    "minutes": component.minutes,
                    "rate_per_minute": rate,
                    "category": component.category or "service",
                    "cost": round(cost, 2),
                    "notes": component.notes,
                }
            )
            total_minutes += component.minutes

        if request.include_subscription:
            automation_minutes = round(total_minutes * 0.2 or 120.0, 2)
            automation_cost = automation_minutes * base_rate
            line_items.append(
                {
                    "name": "Cloud Automation & Monitoring",
                    "minutes": automation_minutes,
                    "rate_per_minute": base_rate,
                    "category": "subscription",
                    "cost": round(automation_cost, 2),
                    "notes": "Always-on OSINT, SEO & Ads Monitoring",
                }
            )
            total_minutes += automation_minutes

        base_cost = sum(item["cost"] for item in line_items)
        margin_amount = round(base_cost * request.margin_percent, 2)
        total_value = round(base_cost + margin_amount, 2)
        summary = request.summary or (
            "Automatisiertes Marketing-, Analytics- und OSINT-Servicepaket mit Echtzeit-Dashboards."
        )

        proposal_payload = ProposalCreate(
            client_id=request.client_id,
            title=request.title,
            summary=summary,
            currency=request.currency,
            line_items=line_items,
            estimated_minutes=round(total_minutes, 2),
            margin_percent=request.margin_percent,
            total_value=total_value,
            status="sent" if request.margin_percent <= 0.25 else "draft",
            valid_until=datetime.utcnow() + timedelta(days=request.valid_days),
            metadata={
                "generated": True,
                "base_cost": base_cost,
                "margin_amount": margin_amount,
            },
        )
        proposal = Proposal(**proposal_payload.dict())
        self.session.add(proposal)
        self.session.commit()
        self.session.refresh(proposal)
        return proposal

    # --- Helpers -----------------------------------------------------------
    def _ensure_client(self, client_id: int) -> Client:
        client = self.session.get(Client, client_id)
        if not client:
            raise ValueError("Client nicht gefunden")
        return client


def serialize_budgets(budgets: List[BudgetAllocation]) -> List[BudgetRead]:
    return [BudgetRead.from_orm(budget) for budget in budgets]


def serialize_invoices(invoices: List[Invoice]) -> List[InvoiceRead]:
    return [InvoiceRead.from_orm(invoice) for invoice in invoices]


def serialize_proposals(proposals: List[Proposal]) -> List[ProposalRead]:
    return [ProposalRead.from_orm(proposal) for proposal in proposals]

