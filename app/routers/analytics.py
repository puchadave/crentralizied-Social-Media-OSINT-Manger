from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..services import mention_volume, sentiment_over_time

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=Dict[str, Dict[str, float]])
async def overview(session: Session = Depends(get_session)) -> Dict[str, Dict[str, float]]:
    volumes = mention_volume(session)
    sentiment_snapshot: Dict[str, float] = {}
    for platform in volumes.keys():
        series = sentiment_over_time(session, platform)["series"]
        sentiment_snapshot[platform] = series[-1]["sentiment"] if series else 0.0
    return {"volume": volumes, "sentiment": sentiment_snapshot}
