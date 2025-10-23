from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import httpx


@dataclass
class CMSResponse:
    status: str
    details: Dict[str, Any]


class CMSConnector:
    base_url: str
    token: str

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    async def patch_metadata(self, resource: str, payload: Dict[str, Any]) -> CMSResponse:
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(f"{self.base_url}/{resource}", json=payload, headers=headers)
            response.raise_for_status()
            return CMSResponse(status="ok", details=response.json())


async def safe_patch(connector: CMSConnector, resource: str, payload: Dict[str, Any]) -> CMSResponse:
    try:
        return await connector.patch_metadata(resource, payload)
    except Exception as exc:  # pragma: no cover - network errors
        return CMSResponse(status="error", details={"error": str(exc)})
