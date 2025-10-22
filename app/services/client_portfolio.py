from __future__ import annotations

from datetime import timedelta
from typing import Iterable, List
from sqlmodel import Session, select

from ..models import (
    BudgetAllocation,
    BudgetRead,
    Client,
    ClientCreate,
    ClientRead,
    ClientSummary,
    Invoice,
    InvoiceRead,
    Proposal,
    ProposalRead,
    Site,
    SiteCreate,
    SiteRead,
)


class ClientPortfolioManager:
    """Verwaltet Mandanten, Multi-Sites und zugehörige Kennzahlen."""

    def __init__(self, session: Session):
        self.session = session

    def _get_client(self, client_id: int) -> Client:
        client = self.session.get(Client, client_id)
        if not client:
            raise ValueError("Client nicht gefunden")
        return client

    def list_clients(self) -> List[Client]:
        statement = select(Client).order_by(Client.created_at.desc())
        return list(self.session.exec(statement).all())

    def create_client(self, payload: ClientCreate) -> Client:
        client = Client(**payload.dict())
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def read_client(self, client_id: int) -> Client:
        return self._get_client(client_id)

    def list_sites(self, client_id: int) -> List[Site]:
        self._get_client(client_id)
        statement = (
            select(Site)
            .where(Site.client_id == client_id)
            .order_by(Site.created_at.desc())
        )
        return list(self.session.exec(statement).all())

    def create_site(self, payload: SiteCreate) -> Site:
        self._get_client(payload.client_id)
        site = Site(**payload.dict())
        if site.api_connected and "analytics" not in site.connected_integrations:
            site.connected_integrations.append("analytics")
        self.session.add(site)
        self.session.commit()
        self.session.refresh(site)
        return site

    def _monthly_equivalent(self, budget: BudgetAllocation) -> float:
        duration: timedelta = budget.period_end - budget.period_start
        days = max(duration.days, 1)
        return budget.allocated_budget * (30 / days)

    def _budgets_for_client(self, client_id: int) -> Iterable[BudgetAllocation]:
        statement = select(BudgetAllocation).where(BudgetAllocation.client_id == client_id)
        return self.session.exec(statement).all()

    def _invoices_for_client(self, client_id: int) -> Iterable[Invoice]:
        statement = select(Invoice).where(Invoice.client_id == client_id)
        return self.session.exec(statement).all()

    def _proposals_for_client(self, client_id: int) -> Iterable[Proposal]:
        statement = select(Proposal).where(Proposal.client_id == client_id)
        return self.session.exec(statement).all()

    def summary(self, client_id: int) -> ClientSummary:
        client = ClientRead.from_orm(self._get_client(client_id))
        sites = [SiteRead.from_orm(site) for site in self.list_sites(client_id)]

        budgets = list(self._budgets_for_client(client_id))
        invoices = list(self._invoices_for_client(client_id))
        proposals = list(self._proposals_for_client(client_id))

        budget_reads = [BudgetRead.from_orm(budget) for budget in budgets]
        invoice_reads = [InvoiceRead.from_orm(invoice) for invoice in invoices]
        proposal_reads = [ProposalRead.from_orm(proposal) for proposal in proposals]

        active_budgets = sum(1 for budget in budgets if budget.status == "active")
        allocated_total = sum(budget.allocated_budget for budget in budgets)
        spent_total = sum(budget.spent_budget for budget in budgets)
        outstanding = sum(
            invoice.amount_due
            for invoice in invoices
            if invoice.status not in {"paid", "cancelled"}
        )
        proposals_progress = sum(
            1 for proposal in proposals if proposal.status in {"draft", "sent"}
        )

        recurring = sum(
            self._monthly_equivalent(budget)
            for budget in budgets
            if budget.status == "active"
        )

        return ClientSummary(
            client=client,
            total_sites=len(sites),
            active_budgets=active_budgets,
            allocated_budget=allocated_total,
            spent_budget=spent_total,
            outstanding_invoices=outstanding,
            proposals_in_progress=proposals_progress,
            monthly_recurring_revenue=recurring,
            budgets=budget_reads,
            invoices=invoice_reads,
            proposals=proposal_reads,
            sites=sites,
        )

