from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..services import (
    dashboard_overview,
    realtime_engagement,
    search_console_snapshot,
    traffic_breakdown,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=Dict[str, Any])
async def overview(session: Session = Depends(get_session)) -> Dict[str, Any]:
    return dashboard_overview(session)


@router.get("/search-console", response_model=Dict[str, Dict[str, float]])
async def search_console(session: Session = Depends(get_session)) -> Dict[str, Dict[str, float]]:
    return search_console_snapshot(session)


@router.get("/traffic", response_model=Dict[str, float])
async def traffic(session: Session = Depends(get_session)) -> Dict[str, float]:
    return traffic_breakdown(session)


@router.get("/engagement", response_model=Dict[str, float])
async def engagement(session: Session = Depends(get_session)) -> Dict[str, float]:
    return realtime_engagement(session)
