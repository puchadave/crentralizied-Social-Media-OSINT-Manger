"""Application bootstrap for the desktop client."""
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QDialog

from ..core.ai import ContentGenerator
from ..core.analytics import AnalyticsService
from ..core.automation import AutomationService
from ..core.config import AppConfig
from ..core.content import ContentRepository
from ..core.external import ExternalAnalysisService
from ..core.seo import SEOOptimizationService

from .main_window import MainWindow
from .setup_wizard import SetupWizard


def run() -> None:
    app = QApplication(sys.argv)
    config = AppConfig.load()
    repository = ContentRepository(config.content_file)
    sample_file = Path(__file__).resolve().parents[2] / "data" / "sample_content.json"
    repository.seed_from(sample_file)

    integrations = config.load_integrations()
    if not integrations.completed:
        wizard = SetupWizard(integrations.clone())
        if wizard.exec() == QDialog.DialogCode.Accepted:
            integrations = wizard.result_settings()
            config.save_integrations(integrations)
        else:
            integrations.ensure_defaults()

    analytics = AnalyticsService()
    automation = AutomationService()
    generator = ContentGenerator()
    seo_service = SEOOptimizationService(generator)
    external_service = ExternalAnalysisService(generator)

    window = MainWindow(
        repository,
        analytics,
        automation,
        generator,
        seo_service,
        external_service,
        config,
        integrations,
    )
    window.show()
    sys.exit(app.exec())


__all__ = ["run"]
