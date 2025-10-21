"""Dashboard widgets for KPIs and monitoring."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..core.analytics import AnalyticsService


class DashboardWidget(QWidget):
    def __init__(self, analytics: AnalyticsService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._analytics = analytics
        self._table = QTableWidget()
        self._chart_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._summary_label = QLabel("Kennzahlen & Trends")
        self._summary_label.setProperty("class", "headline")

        layout = QVBoxLayout(self)
        layout.addWidget(self._summary_label)

        table_container = QWidget()
        table_layout = QHBoxLayout(table_container)
        table_layout.addWidget(self._table)
        table_layout.addWidget(self._chart_canvas)
        layout.addWidget(table_container)

        self._configure_table()
        self.refresh()

    def _configure_table(self) -> None:
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["KPI", "Wert", "Einheit", "Trend %"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

    def refresh(self) -> None:
        kpis = self._analytics.get_kpis()
        self._table.setRowCount(len(kpis))
        for row, kpi in enumerate(kpis):
            self._table.setItem(row, 0, QTableWidgetItem(kpi.name))
            self._table.setItem(row, 1, QTableWidgetItem(f"{kpi.value:,.2f}"))
            self._table.setItem(row, 2, QTableWidgetItem(kpi.unit))
            trend_item = QTableWidgetItem(f"{kpi.trend_percentage:+.1f}%")
            alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            trend_item.setTextAlignment(alignment)
            self._table.setItem(row, 3, trend_item)

        self._plot_timeseries()

    def _plot_timeseries(self) -> None:
        series = self._analytics.engagement_timeseries()
        self._chart_canvas.figure.clear()
        ax = self._chart_canvas.figure.subplots()
        ax.plot([point.timestamp for point in series], [point.value for point in series], marker="o")
        ax.set_title("Engagement (14 Tage)")
        ax.set_ylabel("%")
        ax.grid(True, linestyle="--", alpha=0.4)
        self._chart_canvas.draw_idle()

