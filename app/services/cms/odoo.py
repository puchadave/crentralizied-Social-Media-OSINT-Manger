from __future__ import annotations

from typing import Any, Dict

from .base import CMSConnector, CMSResponse, safe_patch


class OdooConnector(CMSConnector):
    async def update_metadata(self, page_id: int, metadata: Dict[str, Any]) -> CMSResponse:
        resource = f"web/webpage/{page_id}"
        payload = {
            "name": metadata.get("title"),
            "seo_description": metadata.get("description"),
            "seo_keywords": metadata.get("keywords", []),
        }
        return await safe_patch(self, resource, payload)
