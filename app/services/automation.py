from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from sqlmodel import Session, select

from ..models import AutomationRule


class AutomationEngine:
    """Evaluate lightweight automation rules for marketing workflows."""

    def __init__(self, session: Session):
        self.session = session

    def list_rules(self) -> List[AutomationRule]:
        return self.session.exec(select(AutomationRule)).all()

    def create_rule(self, rule: AutomationRule) -> AutomationRule:
        rule.created_at = datetime.utcnow()
        rule.updated_at = datetime.utcnow()
        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        return rule

    def evaluate(self, event: Dict[str, str]) -> List[AutomationRule]:
        matches: List[AutomationRule] = []
        for rule in self.list_rules():
            if not rule.is_active:
                continue
            if rule.trigger != event.get("trigger"):
                continue
            if all(event.get(key) == value for key, value in rule.conditions.items()):
                matches.append(rule)
        return matches

    def toggle_rule(self, rule_id: int, is_active: bool) -> AutomationRule:
        rule = self.session.get(AutomationRule, rule_id)
        if not rule:
            raise ValueError("Automation rule not found")
        rule.is_active = is_active
        rule.updated_at = datetime.utcnow()
        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        return rule
