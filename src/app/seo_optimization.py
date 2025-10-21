"""Widget for AI-assisted SEO optimisation."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.seo import SEOOptimizationService


class SEOOptimizationWidget(QWidget):
    """Surface SEO metrics and allow one-click optimisation."""

    def __init__(self, service: SEOOptimizationService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://www.beispiel.de/")
        self._keywords_input = QLineEdit()
        self._keywords_input.setPlaceholderText("seo automation, marketing intelligence")

        self._metrics_table = QTableWidget()
        self._metrics_table.setColumnCount(4)
        self._metrics_table.setHorizontalHeaderLabels(["Metrik", "Wert", "Einheit", "Trend %"])
        self._metrics_table.verticalHeader().setVisible(False)
        self._metrics_table.horizontalHeader().setStretchLastSection(True)
        self._metrics_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._projected_gain_label = QLabel("Prognostizierter Traffic-Zuwachs: –")

        metrics_box = QGroupBox("Echtzeit-SEO-Metriken")
        metrics_layout = QVBoxLayout(metrics_box)
        metrics_layout.addWidget(self._metrics_table)
        metrics_layout.addWidget(self._projected_gain_label)

        self._refresh_button = QPushButton("Analyse aktualisieren")
        self._refresh_button.clicked.connect(self._refresh_metrics)
        self._optimize_button = QPushButton("AI-Optimierung anwenden")
        self._optimize_button.clicked.connect(self._run_optimization)

        form = QFormLayout()
        form.addRow("Ziel-URL", self._url_input)
        form.addRow("Keywords", self._keywords_input)

        self._meta_description = QLineEdit()
        self._meta_description.setReadOnly(True)

        buttons = QHBoxLayout()
        buttons.addWidget(self._refresh_button)
        buttons.addWidget(self._optimize_button)

        optimization_box = QGroupBox("SEO-Optimierung")
        optimization_layout = QVBoxLayout(optimization_box)
        optimization_layout.addLayout(form)
        optimization_layout.addLayout(buttons)

        meta_layout = QFormLayout()
        meta_layout.addRow("Meta Description", self._meta_description)
        optimization_layout.addLayout(meta_layout)

        self._keyword_list = QListWidget()
        optimization_layout.addWidget(QLabel("Empfohlene Keywords"))
        optimization_layout.addWidget(self._keyword_list)

        self._plan_text = QTextEdit()
        self._plan_text.setReadOnly(True)
        optimization_layout.addWidget(QLabel("Optimierungsplan"))
        optimization_layout.addWidget(self._plan_text)

        self._schema_text = QTextEdit()
        self._schema_text.setReadOnly(True)
        optimization_layout.addWidget(QLabel("Schema Markup Vorschlag"))
        optimization_layout.addWidget(self._schema_text)

        layout = QVBoxLayout(self)
        layout.addWidget(metrics_box)
        layout.addWidget(optimization_box)

        self._timer = QTimer(self)
        self._timer.setInterval(15000)
        self._timer.timeout.connect(self._refresh_metrics)

        self._refresh_metrics()
        self._timer.start()

    def _current_keywords(self) -> list[str]:
        return [kw.strip() for kw in self._keywords_input.text().split(",") if kw.strip()]

    def _refresh_metrics(self) -> None:
        metrics = self._service.realtime_metrics()
        self._metrics_table.setRowCount(len(metrics))
        for row, metric in enumerate(metrics):
            self._metrics_table.setItem(row, 0, QTableWidgetItem(metric.name))
            value_item = QTableWidgetItem(f"{metric.value:,.2f}")
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._metrics_table.setItem(row, 1, value_item)
            self._metrics_table.setItem(row, 2, QTableWidgetItem(metric.unit))
            trend_item = QTableWidgetItem(f"{metric.trend_percentage:+.2f}%")
            trend_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._metrics_table.setItem(row, 3, trend_item)

        keywords = self._current_keywords()
        opportunities = self._service.keyword_opportunities(keywords)
        self._keyword_list.clear()
        for keyword in opportunities:
            self._keyword_list.addItem(keyword)

        projected_gain = self._service.projected_gain(keywords)
        self._projected_gain_label.setText(f"Prognostizierter Traffic-Zuwachs: {projected_gain:+.1f}%")

    def _run_optimization(self) -> None:
        url = self._url_input.text().strip()
        keywords = self._current_keywords()
        plan = self._service.optimization_plan(url, keywords)
        self._plan_text.setPlainText(plan.plan_text)
        self._meta_description.setText(plan.meta_description)
        self._schema_text.setPlainText(plan.structured_data)

        self._keyword_list.clear()
        for keyword in plan.recommended_keywords:
            self._keyword_list.addItem(keyword)

        self._projected_gain_label.setText(
            f"Prognostizierter Traffic-Zuwachs: {plan.projected_gain:+.1f}%"
        )


__all__ = ["SEOOptimizationWidget"]
