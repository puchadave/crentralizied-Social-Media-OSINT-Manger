from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel


class AutomationRuleBase(SQLModel):
    name: str
    trigger: str = Field(description="Trigger identifier, e.g. osint.mention or seo.drop.")
    conditions: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    action: str = Field(description="Action identifier executed when the rule fires.")
    parameters: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = Field(default=True)


class AutomationRule(AutomationRuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AutomationRuleCreate(AutomationRuleBase):
    pass


class AutomationRuleRead(AutomationRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime
