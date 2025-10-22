from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List

from ..models.content import ContentItem


@dataclass
class ConnectorProfile:
    name: str
    features: List[str]
    supports_metadata: bool = True

    def publish(self, item: ContentItem) -> Dict[str, str]:
        """Simulate a publish operation against a social or CMS API."""

        timestamp = datetime.utcnow().isoformat()
        reference = f"{self.name}-{item.id}-{int(datetime.utcnow().timestamp())}"
        status = {
            "status": "dispatched",
            "reference": reference,
            "delivered_at": timestamp,
        }
        if self.supports_metadata and item.metadata:
            status["metadata_applied"] = len(item.metadata)
        status["features"] = self.features
        return status


class SocialNetworkRouter:
    """Central connector registry for Social, CMS und POSITS Netzwerke."""

    def __init__(self, connectors: Iterable[ConnectorProfile] | None = None):
        self._connectors: Dict[str, ConnectorProfile] = {
            profile.name: profile
            for profile in (
                connectors
                if connectors
                else self._default_connectors()
            )
        }

    @staticmethod
    def _default_connectors() -> List[ConnectorProfile]:
        return [
            ConnectorProfile("linkedin", ["organic", "lead_gen"]),
            ConnectorProfile("twitter", ["organic", "spaces"]),
            ConnectorProfile("instagram", ["stories", "reels"]),
            ConnectorProfile("wordpress", ["cms", "metadata"]),
            ConnectorProfile("ghost", ["cms", "newsletter"]),
            ConnectorProfile("odoo", ["cms", "crm_sync"]),
        ]

    def available(self) -> Dict[str, List[str]]:
        return {name: profile.features for name, profile in self._connectors.items()}

    def publish(self, item: ContentItem, networks: Iterable[str]) -> Dict[str, Dict[str, str]]:
        results: Dict[str, Dict[str, str]] = {}
        for network in networks:
            profile = self._connectors.get(network)
            if not profile:
                continue
            results[network] = profile.publish(item)
        return results
