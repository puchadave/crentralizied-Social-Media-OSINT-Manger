"""Main window assembly for the centralized marketing manager."""
from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QMainWindow, QMessageBox, QTabWidget

from ..core.ai import ContentGenerator
from ..core.analytics import AnalyticsService
from ..core.automation import AutomationService
from ..core.config import AppConfig
from ..core.content import ContentRepository
from ..core.external import ExternalAnalysisService
from ..core.integrations import IntegrationSettings
from ..core.seo import SEOOptimizationService
from ..core.social.connectors import build_connectors

from .automation import AutomationWidget
from .content_manager import ContentManagerWidget
from .dashboard import DashboardWidget
from .external_analysis import ExternalAnalysisWidget
from .realtime_analytics import RealTimeAnalyticsWidget
from .seo_optimization import SEOOptimizationWidget
from .setup_wizard import SetupWizard
from .social_monitor import SocialMonitorWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        repository: ContentRepository,
        analytics: AnalyticsService,
        automation: AutomationService,
        generator: ContentGenerator,
        seo_service: SEOOptimizationService,
        external_service: ExternalAnalysisService,
        config: AppConfig,
        integrations: IntegrationSettings,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Crentralized Social Media OSINT Manager")
        self.resize(1280, 800)

        self._config = config
        self._integrations = integrations

        tabs = QTabWidget()
        self._dashboard = DashboardWidget(analytics)
        tabs.addTab(self._dashboard, "Dashboard")

        self._content_manager = ContentManagerWidget(repository, generator, config, integrations)
        tabs.addTab(self._content_manager, "Content Manager")

        self._web_analytics = RealTimeAnalyticsWidget(analytics)
        tabs.addTab(self._web_analytics, "Web Analytics")

        connectors = build_connectors(integrations)
        self._social_monitor = SocialMonitorWidget(connectors)
        tabs.addTab(self._social_monitor, "Social Streams")

        self._automation = AutomationWidget(automation)
        tabs.addTab(self._automation, "Automationen")

        self._seo = SEOOptimizationWidget(seo_service)
        tabs.addTab(self._seo, "SEO Optimierung")

        self._external = ExternalAnalysisWidget(external_service)
        tabs.addTab(self._external, "Außenanalyse")

        self.setCentralWidget(tabs)

        settings_menu = self.menuBar().addMenu("Einstellungen")
        setup_action = settings_menu.addAction("Setup Wizard erneut ausführen…")
        setup_action.triggered.connect(self._launch_setup_wizard)

    def _launch_setup_wizard(self) -> None:  # pragma: no cover - GUI action
        wizard = SetupWizard(self._integrations.clone(), self)
        if wizard.exec() == QDialog.DialogCode.Accepted:
            self._integrations = wizard.result_settings()
            self._config.save_integrations(self._integrations)
            self._content_manager.update_integrations(self._integrations)
            connectors = build_connectors(self._integrations)
            self._social_monitor.update_connectors(connectors)
            QMessageBox.information(
                self,
                "Setup aktualisiert",
                "Die Integrationen wurden erfolgreich aktualisiert.",
            )

