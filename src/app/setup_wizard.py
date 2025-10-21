"""Step-by-step wizard for onboarding API integrations."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from ..core.integrations import (
    IntegrationSettings,
    MEDIA_PROVIDER_DEFINITIONS,
    SOCIAL_NETWORK_DEFINITIONS,
    VIDEO_GENERATOR_DEFINITIONS,
)


class _IntroPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Willkommen zum Einrichtungsassistenten")
        label = QLabel(
            "Dieser Assistent führt Sie Schritt für Schritt durch die API-Anbindung aller Social-"
            "Media-Konten, Medienbibliotheken und des SORA II Video Generators. Die Eingaben werden "
            "verschlüsselt in Ihrer lokalen Konfiguration gespeichert."
        )
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class _IntegrationPage(QWizardPage):
    def __init__(
        self,
        category: str,
        name: str,
        fields: list[str],
        existing: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.category = category
        self.integration_name = name
        self._inputs: dict[str, QLineEdit] = {}
        self.setTitle(f"{name} verbinden")
        self.setSubTitle("Tragen Sie die benötigten API-Zugangsdaten ein.")

        layout = QFormLayout()
        sanitized_existing = {k: v for k, v in (existing or {}).items() if k != "status"}
        for field in fields:
            line = QLineEdit(sanitized_existing.get(field, ""))
            line.setPlaceholderText(field)
            layout.addRow(field, line)
            self._inputs[field] = line
        self.setLayout(layout)

    def values(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for field, widget in self._inputs.items():
            value = widget.text().strip()
            if value:
                result[field] = value
        return result


class _SummaryPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Abschluss")
        label = QLabel(
            "Vielen Dank! Mit \"Fertigstellen\" werden die Verbindungen gespeichert und stehen in der "
            "Oberfläche sofort zur Verfügung."
        )
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class SetupWizard(QWizard):
    def __init__(self, settings: IntegrationSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("API Setup Wizard")
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self._initial = settings
        self._result = settings

        self.addPage(_IntroPage())

        self._integration_pages: list[_IntegrationPage] = []
        for definition in SOCIAL_NETWORK_DEFINITIONS:
            page = _IntegrationPage(
                "social",
                definition["name"],
                definition["fields"],
                settings.social_credentials.get(definition["name"], {}),
            )
            self._integration_pages.append(page)
            self.addPage(page)

        for definition in MEDIA_PROVIDER_DEFINITIONS:
            page = _IntegrationPage(
                "media",
                definition["name"],
                definition["fields"],
                settings.media_providers.get(definition["name"], {}),
            )
            self._integration_pages.append(page)
            self.addPage(page)

        for definition in VIDEO_GENERATOR_DEFINITIONS:
            page = _IntegrationPage(
                "video",
                definition["name"],
                definition["fields"],
                settings.video_generators.get(definition["name"], {}),
            )
            self._integration_pages.append(page)
            self.addPage(page)

        self.addPage(_SummaryPage())

    def accept(self) -> None:  # pragma: no cover - GUI action
        self._result = self._collect_results()
        super().accept()

    def result_settings(self) -> IntegrationSettings:
        return self._result

    def _collect_results(self) -> IntegrationSettings:
        updated = self._initial.clone()
        updated.ensure_defaults()
        for page in self._integration_pages:
            values = page.values()
            if values:
                updated.mark_connected(page.category, page.integration_name, values)
        updated.completed = True
        return updated


__all__ = ["SetupWizard"]
