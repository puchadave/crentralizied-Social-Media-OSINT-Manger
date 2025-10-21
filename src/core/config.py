"""Configuration helpers for the desktop application."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os

from .integrations import IntegrationSettings


@dataclass(slots=True)
class AppConfig:
    data_dir: Path
    content_file: Path
    integrations_file: Path

    @classmethod
    def load(cls) -> "AppConfig":
        base_dir = Path(os.getenv("APP_DATA_DIR", Path.home() / ".crentralized_osint"))
        base_dir.mkdir(parents=True, exist_ok=True)
        content_file = Path(os.getenv("CONTENT_STORE", base_dir / "content.json"))
        integrations_file = Path(
            os.getenv("INTEGRATIONS_STORE", base_dir / "integrations.json")
        )
        return cls(
            data_dir=base_dir,
            content_file=content_file,
            integrations_file=integrations_file,
        )

    def load_integrations(self) -> IntegrationSettings:
        if self.integrations_file.exists():
            data = json.loads(self.integrations_file.read_text(encoding="utf-8"))
            settings = IntegrationSettings.from_dict(data)
        else:
            settings = IntegrationSettings()
        settings.ensure_defaults()
        return settings

    def save_integrations(self, settings: IntegrationSettings) -> None:
        self.integrations_file.write_text(
            json.dumps(settings.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "data_dir": str(self.data_dir),
                "content_file": str(self.content_file),
                "integrations_file": str(self.integrations_file),
            }
        )


__all__ = ["AppConfig"]
