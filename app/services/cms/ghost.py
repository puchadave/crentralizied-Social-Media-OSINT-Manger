from __future__ import annotations

from typing import Any, Dict

from .base import CMSConnector, CMSResponse, safe_patch


class GhostConnector(CMSConnector):
    async def update_page_metadata(self, page_id: str, metadata: Dict[str, Any]) -> CMSResponse:
        resource = f"ghost/api/admin/pages/{page_id}"
        payload = {
            "pages": [
                {
                    "id": page_id,
                    "title": metadata.get("title"),
                    "custom_excerpt": metadata.get("description"),
                    "meta_title": metadata.get("title"),
                    "meta_description": metadata.get("description"),
                }
            ]
        }
        return await safe_patch(self, resource, payload)
