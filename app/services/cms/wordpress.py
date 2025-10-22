from __future__ import annotations

from typing import Any, Dict

from .base import CMSConnector, CMSResponse, safe_patch


class WordPressConnector(CMSConnector):
    async def update_post_metadata(self, post_id: int, metadata: Dict[str, Any]) -> CMSResponse:
        resource = f"wp-json/wp/v2/posts/{post_id}"
        payload = {
            "title": metadata.get("title"),
            "meta": {
                "_yoast_wpseo_metadesc": metadata.get("description"),
                "_yoast_wpseo_focuskw": ",".join(metadata.get("keywords", [])),
            },
        }
        return await safe_patch(self, resource, payload)
