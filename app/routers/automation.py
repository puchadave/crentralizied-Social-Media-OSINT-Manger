from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import AutomationRule, AutomationRuleCreate, AutomationRuleRead
from ..services.automation import AutomationEngine

router = APIRouter(prefix="/automation", tags=["automation"])


def get_engine(session: Session = Depends(get_session)) -> AutomationEngine:
    return AutomationEngine(session)


@router.get("/", response_model=List[AutomationRuleRead])
async def list_rules(engine: AutomationEngine = Depends(get_engine)) -> List[AutomationRule]:
    return engine.list_rules()


@router.post("/", response_model=AutomationRuleRead)
async def create_rule(
    payload: AutomationRuleCreate,
    engine: AutomationEngine = Depends(get_engine),
) -> AutomationRule:
    rule = AutomationRule.from_orm(payload)
    return engine.create_rule(rule)


@router.post("/{rule_id}/toggle", response_model=AutomationRuleRead)
async def toggle_rule(
    rule_id: int,
    is_active: bool,
    engine: AutomationEngine = Depends(get_engine),
) -> AutomationRule:
    try:
        return engine.toggle_rule(rule_id, is_active)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/evaluate", response_model=List[AutomationRuleRead])
async def evaluate_event(
    event: Dict[str, str],
    engine: AutomationEngine = Depends(get_engine),
) -> List[AutomationRule]:
    return engine.evaluate(event)
