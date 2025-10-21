"""Widget for real-time external reach analytics and optimisation."""
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

from ..core.external import ExternalAnalysisService


class ExternalAnalysisWidget(QWidget):
    """Live overview of off-site performance with optimisation hints."""

    def __init__(self, service: ExternalAnalysisService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._timer = QTimer(self)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self.refresh)

        self._last_update = QLabel("Letztes Update: –")
        self._refresh_button = QPushButton("Analyse aktualisieren")
        self._refresh_button.clicked.connect(self.refresh)

        self._metrics_table = QTableWidget()
        self._metrics_table.setColumnCount(5)
        self._metrics_table.setHorizontalHeaderLabels(
            [
                "Netzwerk",
                "Share of Voice %",
                "Sentiment",
                "Erwähnungen/h",
                "Trend %",
            ]
        )
        self._metrics_table.verticalHeader().setVisible(False)
        self._metrics_table.horizontalHeader().setStretchLastSection(True)
        self._metrics_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._chart_canvas = FigureCanvas(Figure(figsize=(6, 3)))

        self._recommendation_table = QTableWidget()
        self._recommendation_table.setColumnCount(4)
        self._recommendation_table.setHorizontalHeaderLabels(
            ["Netzwerk", "Empfehlung", "Erwarteter Reach-Boost %", "Hashtags"]
        )
        self._recommendation_table.verticalHeader().setVisible(False)
        self._recommendation_table.horizontalHeader().setStretchLastSection(True)
        self._recommendation_table.setWordWrap(True)
        self._recommendation_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._last_update)
        header_layout.addStretch(1)
        header_layout.addWidget(self._refresh_button)

        layout = QVBoxLayout(self)
        layout.addLayout(header_layout)
        layout.addWidget(self._metrics_table)
        layout.addWidget(self._chart_canvas)
        layout.addWidget(self._recommendation_table)

        self.refresh()
        self._timer.start()

    def refresh(self) -> None:
        metrics = self._service.realtime_metrics()
        self._populate_metrics(metrics)
        self._update_chart()
        self._populate_recommendations(metrics)
        self._last_update.setText(f"Letztes Update: {datetime.utcnow().strftime('%H:%M:%S UTC')}")

    def _populate_metrics(self, metrics) -> None:
        self._metrics_table.setRowCount(len(metrics))
        for row, metric in enumerate(metrics):
            self._metrics_table.setItem(row, 0, QTableWidgetItem(metric.network))
            self._metrics_table.setItem(row, 1, self._format_number(metric.share_of_voice))
            self._metrics_table.setItem(row, 2, self._format_number(metric.sentiment))
            self._metrics_table.setItem(row, 3, self._format_number(metric.mentions_per_hour))
            self._metrics_table.setItem(row, 4, self._format_number(metric.trend_percentage, prefix="+"))

    def _populate_recommendations(self, metrics) -> None:
        recommendations = self._service.optimization_recommendations(metrics)
        self._recommendation_table.setRowCount(len(recommendations))
        for row, recommendation in enumerate(recommendations):
            self._recommendation_table.setItem(row, 0, QTableWidgetItem(recommendation.network))
            action_item = QTableWidgetItem(recommendation.action)
            action_item.setFlags(action_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._recommendation_table.setItem(row, 1, action_item)

            gain_item = self._format_number(recommendation.expected_gain, prefix="+")
            gain_item.setData(Qt.ItemDataRole.UserRole, recommendation.expected_gain)
            self._recommendation_table.setItem(row, 2, gain_item)

            hashtags_text = ", ".join(recommendation.hashtags)
            hashtags_item = QTableWidgetItem(hashtags_text)
            hashtags_item.setFlags(hashtags_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._recommendation_table.setItem(row, 3, hashtags_item)

        self._recommendation_table.resizeRowsToContents()

    def _update_chart(self) -> None:
        data = self._service.share_of_voice_timeseries()
        self._chart_canvas.figure.clear()
        ax = self._chart_canvas.figure.subplots()
        for network, series in data.items():
            if not series:
                continue
            ax.plot(
                [point.timestamp for point in series],
                [point.value for point in series],
                label=network,
            )
        ax.set_title("Share of Voice – letzte 90 Minuten")
        ax.set_ylabel("Prozent")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper right", ncol=2)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
        self._chart_canvas.figure.tight_layout()
        self._chart_canvas.draw_idle()

    @staticmethod
    def _format_number(value: float, prefix: str = "") -> QTableWidgetItem:
        item = QTableWidgetItem(f"{prefix}{value:,.2f}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item


__all__ = ["ExternalAnalysisWidget"]

