from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from ..database import get_session
from ..models import (
    BudgetCreate,
    BudgetRead,
    InvoiceCreate,
    InvoiceRead,
    ProposalGenerationRequest,
    ProposalRead,
)
from ..services.billing import (
    BillingEngine,
    serialize_budgets,
    serialize_invoices,
    serialize_proposals,
)

router = APIRouter(prefix="/billing", tags=["billing"])


class SpendAdjustment(BaseModel):
    delta: float


class StatusChange(BaseModel):
    status: str


def get_engine(session: Session = Depends(get_session)) -> BillingEngine:
    return BillingEngine(session)


@router.get("/budgets", response_model=List[BudgetRead])
async def list_budgets(
    client_id: Optional[int] = None,
    engine: BillingEngine = Depends(get_engine),
) -> List[BudgetRead]:
    budgets = engine.list_budgets(client_id=client_id)
    return serialize_budgets(budgets)


@router.post("/budgets", response_model=BudgetRead)
async def create_budget(
    payload: BudgetCreate, engine: BillingEngine = Depends(get_engine)
) -> BudgetRead:
    try:
        budget = engine.create_budget(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BudgetRead.from_orm(budget)


@router.post("/budgets/{budget_id}/spend", response_model=BudgetRead)
async def update_spend(
    budget_id: int,
    adjustment: SpendAdjustment,
    engine: BillingEngine = Depends(get_engine),
) -> BudgetRead:
    try:
        budget = engine.record_spend(budget_id, adjustment.delta)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return BudgetRead.from_orm(budget)


@router.get("/invoices", response_model=List[InvoiceRead])
async def list_invoices(
    client_id: Optional[int] = None,
    engine: BillingEngine = Depends(get_engine),
) -> List[InvoiceRead]:
    invoices = engine.list_invoices(client_id=client_id)
    return serialize_invoices(invoices)


@router.post("/invoices", response_model=InvoiceRead)
async def create_invoice(
    payload: InvoiceCreate, engine: BillingEngine = Depends(get_engine)
) -> InvoiceRead:
    try:
        invoice = engine.create_invoice(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return InvoiceRead.from_orm(invoice)


@router.post("/invoices/{invoice_id}/status", response_model=InvoiceRead)
async def set_status(
    invoice_id: int,
    change: StatusChange,
    engine: BillingEngine = Depends(get_engine),
) -> InvoiceRead:
    try:
        invoice = engine.set_invoice_status(invoice_id, change.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return InvoiceRead.from_orm(invoice)


@router.get("/proposals", response_model=List[ProposalRead])
async def list_proposals(
    client_id: Optional[int] = None,
    engine: BillingEngine = Depends(get_engine),
) -> List[ProposalRead]:
    proposals = engine.list_proposals(client_id=client_id)
    return serialize_proposals(proposals)


@router.post("/proposals/generate", response_model=ProposalRead)
async def generate_proposal(
    payload: ProposalGenerationRequest, engine: BillingEngine = Depends(get_engine)
) -> ProposalRead:
    try:
        proposal = engine.generate_proposal(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProposalRead.from_orm(proposal)

