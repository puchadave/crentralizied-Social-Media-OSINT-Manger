"""GUI for managing reusable marketing content."""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.content import ContentRepository
from ..core.ai import ContentGenerator
from ..core.config import AppConfig
from ..core.integrations import (
    IntegrationSettings,
    MEDIA_PROVIDER_DEFINITIONS,
    VIDEO_GENERATOR_DEFINITIONS,
)


class ContentManagerWidget(QWidget):
    def __init__(
        self,
        repository: ContentRepository,
        generator: ContentGenerator,
        config: AppConfig,
        integrations: IntegrationSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repository = repository
        self._generator = generator
        self._config = config
        self._integrations = integrations

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            "Titel",
            "Netzwerke",
            "Erstellt",
            "Geplant",
            "Tags",
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._title_input = QLineEdit()
        self._body_input = QTextEdit()
        self._networks_input = QLineEdit()
        self._tags_input = QLineEdit()

        form = QFormLayout()
        form.addRow("Titel", self._title_input)
        form.addRow("Inhalt", self._body_input)
        form.addRow("Netzwerke (Komma)", self._networks_input)
        form.addRow("Tags", self._tags_input)

        self._generate_button = QPushButton("AI-Vorschlag")
        self._video_button = QPushButton("SORA II Video entwerfen")
        self._save_button = QPushButton("Speichern")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self._generate_button)
        button_layout.addWidget(self._video_button)
        button_layout.addWidget(self._save_button)

        form_box = QGroupBox("Neuen Content anlegen")
        form_layout = QVBoxLayout(form_box)
        form_layout.addLayout(form)
        form_layout.addLayout(button_layout)

        self._media_status_labels: dict[str, QLabel] = {}
        media_box = self._build_media_box()
        video_box = self._build_video_box()

        layout = QVBoxLayout(self)
        layout.addWidget(self._table)
        layout.addWidget(form_box)
        layout.addWidget(media_box)
        layout.addWidget(video_box)

        self._generate_button.clicked.connect(self._on_generate_clicked)
        self._save_button.clicked.connect(self._on_save_clicked)
        self._video_button.clicked.connect(self._on_video_clicked)

        self.refresh()
        self._refresh_all_media()
        self._refresh_video_status()

    def refresh(self) -> None:
        items = self._repository.all()
        self._table.setRowCount(len(items))
        for row, item in enumerate(items):
            self._table.setItem(row, 0, QTableWidgetItem(item.title))
            self._table.setItem(row, 1, QTableWidgetItem(", ".join(item.networks)))
            self._table.setItem(row, 2, QTableWidgetItem(item.created_at.strftime("%Y-%m-%d %H:%M")))
            scheduled = item.scheduled_for.strftime("%Y-%m-%d %H:%M") if item.scheduled_for else "-"
            self._table.setItem(row, 3, QTableWidgetItem(scheduled))
            self._table.setItem(row, 4, QTableWidgetItem(", ".join(item.tags)))

    def update_integrations(self, integrations: IntegrationSettings) -> None:
        self._integrations = integrations
        self._refresh_all_media()
        self._refresh_video_status()

    def _on_generate_clicked(self) -> None:
        brief = self._title_input.text() or "Social Media Kampagne"
        tone = "informativer Ton"
        draft = self._generator.draft_post(brief, tone=tone)
        self._body_input.setPlainText(draft)
        if not self._tags_input.text():
            hashtags = self._generator.suggest_hashtags(brief.split())
            self._tags_input.setText(", ".join(hashtags))

    def _on_video_clicked(self) -> None:
        title = self._title_input.text().strip() or "Video Kampagne"
        duration, ok = QInputDialog.getInt(
            self,
            "SORA II Dauer",
            "Videolänge in Sekunden:",
            value=30,
            min=5,
            max=300,
            step=5,
        )
        if not ok:
            return
        storyboard = self._generator.generate_video_storyboard(title, duration=duration)
        self._body_input.setPlainText(storyboard)
        current_tags = {tag.strip().lower() for tag in self._tags_input.text().split(",") if tag.strip()}
        if "#video" not in current_tags:
            current_tags.add("#video")
            self._tags_input.setText(", ".join(sorted(current_tags)))
        QMessageBox.information(
            self,
            "SORA II Storyboard",
            "Das erzeugte Storyboard wurde in das Inhaltsfeld übernommen.",
        )

    def _on_save_clicked(self) -> None:
        title = self._title_input.text().strip()
        body = self._body_input.toPlainText().strip()
        networks = [name.strip() for name in self._networks_input.text().split(",") if name.strip()]
        tags = [tag.strip() for tag in self._tags_input.text().split(",") if tag.strip()]

        if not title or not body:
            return

        scheduled_time = datetime.utcnow()
        self._repository.add_content(title, body, networks or ["All"], tags=tags, scheduled_for=scheduled_time)
        self._clear_inputs()
        self.refresh()

    def _clear_inputs(self) -> None:
        self._title_input.clear()
        self._body_input.clear()
        self._networks_input.clear()
        self._tags_input.clear()

    def _build_media_box(self) -> QGroupBox:
        box = QGroupBox("Medienbibliotheken")
        layout = QFormLayout(box)
        for definition in MEDIA_PROVIDER_DEFINITIONS:
            name = definition["name"]
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            status_label = QLabel()
            status_label.setObjectName(f"status_{name}")
            button = QPushButton("Konfigurieren")
            button.clicked.connect(
                lambda _=False, service=name, fields=list(definition["fields"]): self._configure_media_service(service, fields)
            )
            row_layout.addWidget(status_label)
            row_layout.addWidget(button)
            layout.addRow(name, row_widget)
            self._media_status_labels[name] = status_label
        return box

    def _build_video_box(self) -> QGroupBox:
        box = QGroupBox("SORA II Video Generator")
        layout = QVBoxLayout(box)
        self._video_status_label = QLabel()
        layout.addWidget(self._video_status_label)
        if VIDEO_GENERATOR_DEFINITIONS:
            fields = list(VIDEO_GENERATOR_DEFINITIONS[0]["fields"])
            configure_button = QPushButton("API konfigurieren")
            configure_button.clicked.connect(
                lambda _=False, provider=VIDEO_GENERATOR_DEFINITIONS[0]["name"], params=fields: self._configure_video_provider(provider, params)
            )
            layout.addWidget(configure_button)
        return box

    def _configure_media_service(self, service: str, fields: list[str]) -> None:
        payload: dict[str, str] = {}
        for field in fields:
            value, ok = QInputDialog.getText(
                self,
                f"{service}: {field}",
                f"Bitte {field} eintragen:",
            )
            if not ok:
                return
            value = value.strip()
            if not value:
                QMessageBox.warning(self, "Ungültige Eingabe", f"{field} darf nicht leer sein.")
                return
            payload[field] = value
        self._integrations.mark_connected("media", service, payload)
        self._persist_integrations()
        self._refresh_media_status(service)
        QMessageBox.information(self, "Integration gespeichert", f"{service} wurde verbunden.")

    def _configure_video_provider(self, provider: str, fields: list[str]) -> None:
        payload: dict[str, str] = {}
        for field in fields:
            value, ok = QInputDialog.getText(
                self,
                f"{provider}: {field}",
                f"Bitte {field} eintragen:",
            )
            if not ok:
                return
            value = value.strip()
            if not value:
                QMessageBox.warning(self, "Ungültige Eingabe", f"{field} darf nicht leer sein.")
                return
            payload[field] = value
        self._integrations.mark_connected("video", provider, payload)
        self._persist_integrations()
        self._refresh_video_status()
        QMessageBox.information(self, "Integration gespeichert", f"{provider} wurde verbunden.")

    def _persist_integrations(self) -> None:
        self._config.save_integrations(self._integrations)

    def _refresh_all_media(self) -> None:
        for definition in MEDIA_PROVIDER_DEFINITIONS:
            self._refresh_media_status(definition["name"])

    def _refresh_media_status(self, service: str) -> None:
        status_label = self._media_status_labels.get(service)
        if not status_label:
            return
        status_label.setText(self._format_status_text("media", service))

    def _refresh_video_status(self) -> None:
        if hasattr(self, "_video_status_label"):
            self._video_status_label.setText(self._format_status_text("video", "SORA II"))

    def _format_status_text(self, category: str, name: str) -> str:
        status = self._integrations.status_for(category, name)
        mapping = {
            "connected": "Verbunden",
            "disconnected": "Getrennt",
            "unconfigured": "Nicht konfiguriert",
        }
        return mapping.get(status, status)


