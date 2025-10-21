"""Integration catalogues and persisted state helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping

SOCIAL_NETWORK_DEFINITIONS = [
    {"name": "Facebook", "fields": ["App ID", "App Secret"]},
    {"name": "Facebook Business", "fields": ["System User Token", "Ad Account ID"]},
    {"name": "Instagram", "fields": ["Client ID", "Client Secret"]},
    {"name": "Instagram Business", "fields": ["Business ID", "Access Token"]},
    {"name": "LinkedIn", "fields": ["Client ID", "Client Secret"]},
    {"name": "X", "fields": ["API Key", "API Secret", "Bearer Token"]},
    {"name": "TikTok", "fields": ["Client Key", "Client Secret"]},
    {"name": "YouTube", "fields": ["API Key"]},
    {"name": "Mastodon", "fields": ["Server URL", "Access Token"]},
    {"name": "Snapchat", "fields": ["Client ID", "Client Secret"]},
    {"name": "WhatsApp", "fields": ["Phone Number ID", "Access Token"]},
    {"name": "WhatsApp Business", "fields": ["Business Account ID", "Access Token"]},
    {"name": "Reddit", "fields": ["Client ID", "Client Secret"]},
    {"name": "Medium", "fields": ["Integration Token"]},
]

MEDIA_PROVIDER_DEFINITIONS = [
    {"name": "Google Photos", "fields": ["OAuth Client ID", "OAuth Client Secret"]},
    {"name": "Unsplash", "fields": ["Access Key", "Secret Key"]},
    {"name": "Pexels", "fields": ["API Key"]},
]

VIDEO_GENERATOR_DEFINITIONS = [
    {"name": "SORA II", "fields": ["API Key", "Model"]},
]


@dataclass(slots=True)
class IntegrationSettings:
    """Persisted API credentials and connection metadata."""

    social_credentials: dict[str, dict[str, str]] = field(default_factory=dict)
    media_providers: dict[str, dict[str, str]] = field(default_factory=dict)
    video_generators: dict[str, dict[str, str]] = field(default_factory=dict)
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "social_credentials": {name: dict(meta) for name, meta in self.social_credentials.items()},
            "media_providers": {name: dict(meta) for name, meta in self.media_providers.items()},
            "video_generators": {name: dict(meta) for name, meta in self.video_generators.items()},
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "IntegrationSettings":
        return cls(
            social_credentials={
                str(name): dict(meta)
                for name, meta in data.get("social_credentials", {}).items()
            },
            media_providers={
                str(name): dict(meta)
                for name, meta in data.get("media_providers", {}).items()
            },
            video_generators={
                str(name): dict(meta)
                for name, meta in data.get("video_generators", {}).items()
            },
            completed=bool(data.get("completed", False)),
        )

    def clone(self) -> "IntegrationSettings":
        return IntegrationSettings.from_dict(self.to_dict())

    def ensure_defaults(self) -> None:
        for definition in SOCIAL_NETWORK_DEFINITIONS:
            self.social_credentials.setdefault(definition["name"], {"status": "unconfigured"})
        for definition in MEDIA_PROVIDER_DEFINITIONS:
            self.media_providers.setdefault(definition["name"], {"status": "unconfigured"})
        for definition in VIDEO_GENERATOR_DEFINITIONS:
            self.video_generators.setdefault(definition["name"], {"status": "unconfigured"})

    def _store_for(self, category: str) -> MutableMapping[str, dict[str, str]]:
        if category == "social":
            return self.social_credentials
        if category == "media":
            return self.media_providers
        if category == "video":
            return self.video_generators
        raise ValueError(f"Unbekannte Integrationskategorie: {category}")

    def mark_connected(
        self,
        category: str,
        name: str,
        payload: Mapping[str, str] | None = None,
    ) -> None:
        store = self._store_for(category)
        data = dict(payload or {})
        data["status"] = "connected"
        store[name] = data

    def mark_disconnected(self, category: str, name: str) -> None:
        self._store_for(category)[name] = {"status": "disconnected"}

    def status_for(self, category: str, name: str) -> str:
        store = self._store_for(category)
        return store.get(name, {}).get("status", "unconfigured")

    def connected_networks(self) -> list[str]:
        return [
            name
            for name, meta in self.social_credentials.items()
            if meta.get("status") == "connected"
        ]


__all__ = [
    "IntegrationSettings",
    "SOCIAL_NETWORK_DEFINITIONS",
    "MEDIA_PROVIDER_DEFINITIONS",
    "VIDEO_GENERATOR_DEFINITIONS",
]
