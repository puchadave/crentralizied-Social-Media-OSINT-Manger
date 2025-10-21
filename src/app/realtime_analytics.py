"""Widget that displays real-time website analytics."""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..core.analytics import AnalyticsService


class RealTimeAnalyticsWidget(QWidget):
    """Live metrics for on-site behaviour, refreshed automatically."""

    def __init__(self, analytics: AnalyticsService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._analytics = analytics
        self._timer = QTimer(self)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self.refresh)

        self._last_update_label = QLabel("Letztes Update: –")
        self._metrics_table = QTableWidget()
        self._metrics_table.setColumnCount(4)
        self._metrics_table.setHorizontalHeaderLabels(["Metrik", "Wert", "Einheit", "Trend %"])
        self._metrics_table.verticalHeader().setVisible(False)
        self._metrics_table.horizontalHeader().setStretchLastSection(True)
        self._metrics_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._chart_canvas = FigureCanvas(Figure(figsize=(6, 3)))

        self._refresh_button = QPushButton("Jetzt aktualisieren")
        self._refresh_button.clicked.connect(self.refresh)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._last_update_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self._refresh_button)

        layout = QVBoxLayout(self)
        layout.addLayout(header_layout)
        layout.addWidget(self._metrics_table)
        layout.addWidget(self._chart_canvas)

        self.refresh()
        self._timer.start()

    def refresh(self) -> None:
        metrics = self._analytics.web_realtime_metrics()
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

        series = self._analytics.web_sessions_timeseries()
        self._chart_canvas.figure.clear()
        ax = self._chart_canvas.figure.subplots()
        ax.plot(
            [point.timestamp for point in series],
            [point.value for point in series],
            marker="o",
        )
        ax.set_title("Aktive Sitzungen (letzte 60 Minuten)")
        ax.set_ylabel("Besucher")
        ax.grid(True, linestyle="--", alpha=0.4)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
        self._chart_canvas.figure.tight_layout()
        self._chart_canvas.draw_idle()

        self._last_update_label.setText(f"Letztes Update: {datetime.utcnow().strftime('%H:%M:%S UTC')}")


__all__ = ["RealTimeAnalyticsWidget"]
