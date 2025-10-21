"""Widget to display and manage automation pipelines."""
from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from ..core.automation import AutomationService, AutomationTask


class AutomationWidget(QWidget):
    def __init__(self, service: AutomationService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._tasks_list = QListWidget()
        self._toggle_button = QPushButton("Status umschalten")

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Geplante Automationen"))
        top_layout.addStretch(1)
        top_layout.addWidget(self._toggle_button)

        layout = QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addWidget(self._tasks_list)

        self._toggle_button.clicked.connect(self._on_toggle_clicked)

        self.refresh()

    def refresh(self) -> None:
        self._tasks_list.clear()
        for task in self._service.all():
            label = self._format_task(task)
            item = QListWidgetItem(label)
            item.setData(1001, task.name)
            self._tasks_list.addItem(item)
        if self._tasks_list.count():
            self._tasks_list.setCurrentRow(0)

    def _format_task(self, task: AutomationTask) -> str:
        cadence_hours = task.cadence.total_seconds() / 3600
        cadence = f"alle {cadence_hours:.1f}h" if cadence_hours < 24 else f"alle {cadence_hours/24:.0f} Tage"
        status = "Aktiv" if task.active else "Pausiert"
        return f"{task.name} — {status}\n{task.description}\nNächster Lauf: {task.next_run:%Y-%m-%d %H:%M} ({cadence})"

    def _on_toggle_clicked(self) -> None:
        current = self._tasks_list.currentItem()
        if not current:
            return
        task_name = current.data(1001)
        for task in self._service.all():
            if task.name == task_name:
                self._service.toggle(task.name, not task.active)
                break
        self.refresh()

