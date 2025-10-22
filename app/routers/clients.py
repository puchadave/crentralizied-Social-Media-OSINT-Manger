from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import ClientCreate, ClientRead, ClientSummary, SiteCreate, SiteRead
from ..services.client_portfolio import ClientPortfolioManager

router = APIRouter(prefix="/clients", tags=["clients"])


def get_manager(session: Session = Depends(get_session)) -> ClientPortfolioManager:
    return ClientPortfolioManager(session)


@router.get("/", response_model=List[ClientRead])
async def list_clients(manager: ClientPortfolioManager = Depends(get_manager)) -> List[ClientRead]:
    clients = manager.list_clients()
    return [ClientRead.from_orm(client) for client in clients]


@router.post("/", response_model=ClientRead)
async def create_client(
    payload: ClientCreate, manager: ClientPortfolioManager = Depends(get_manager)
) -> ClientRead:
    client = manager.create_client(payload)
    return ClientRead.from_orm(client)


@router.get("/{client_id}", response_model=ClientRead)
async def read_client(
    client_id: int, manager: ClientPortfolioManager = Depends(get_manager)
) -> ClientRead:
    try:
        client = manager.read_client(client_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ClientRead.from_orm(client)


@router.get("/{client_id}/sites", response_model=List[SiteRead])
async def list_sites(
    client_id: int, manager: ClientPortfolioManager = Depends(get_manager)
) -> List[SiteRead]:
    try:
        sites = manager.list_sites(client_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [SiteRead.from_orm(site) for site in sites]


@router.post("/{client_id}/sites", response_model=SiteRead)
async def create_site(
    client_id: int,
    payload: SiteCreate,
    manager: ClientPortfolioManager = Depends(get_manager),
) -> SiteRead:
    try:
        payload.client_id = client_id
        site = manager.create_site(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SiteRead.from_orm(site)


@router.get("/{client_id}/summary", response_model=ClientSummary)
async def client_summary(
    client_id: int, manager: ClientPortfolioManager = Depends(get_manager)
) -> ClientSummary:
    try:
        return manager.summary(client_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

