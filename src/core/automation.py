"""Automation helper for scheduling and monitoring outbound campaigns."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(slots=True)
class AutomationTask:
    name: str
    description: str
    next_run: datetime
    cadence: timedelta
    active: bool = True


class AutomationService:
    def __init__(self) -> None:
        self._tasks: list[AutomationTask] = [
            AutomationTask(
                name="Daily KPI Snapshot",
                description="Collect KPIs from all networks and update dashboard.",
                next_run=datetime.utcnow().replace(hour=6, minute=0, second=0, microsecond=0),
                cadence=timedelta(days=1),
            ),
            AutomationTask(
                name="Weekly Newsletter",
                description="Generate newsletter draft with OpenAI and schedule for approval.",
                next_run=datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0),
                cadence=timedelta(days=7),
            ),
            AutomationTask(
                name="Cross-Posting",
                description="Publish approved content to all selected social networks.",
                next_run=datetime.utcnow().replace(hour=9, minute=30, second=0, microsecond=0),
                cadence=timedelta(hours=4),
            ),
        ]

    def all(self) -> list[AutomationTask]:
        return list(self._tasks)

    def toggle(self, name: str, active: bool) -> None:
        for task in self._tasks:
            if task.name == name:
                task.active = active
                break

    def register(self, task: AutomationTask) -> None:
        self._tasks.append(task)

    def upcoming(self, within: timedelta) -> list[AutomationTask]:
        threshold = datetime.utcnow() + within
        return [task for task in self._tasks if task.next_run <= threshold]

