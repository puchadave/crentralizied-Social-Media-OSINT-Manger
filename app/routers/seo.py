from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..models import MetadataPatch, SEOReportRead
from ..services import analyse_url, push_metadata_patch

router = APIRouter(prefix="/seo", tags=["seo"])


@router.post("/analyse", response_model=SEOReportRead)
async def analyse_endpoint(url: str, session: Session = Depends(get_session)):
    report = await analyse_url(session, url)
    return report


@router.post("/metadata", response_model=MetadataPatch)
async def update_metadata(patch: MetadataPatch, session: Session = Depends(get_session)):
    stored_patch = await push_metadata_patch(session, patch)
    return stored_patch


@router.post("/metadata/cms", response_model=Dict[str, str])
async def update_cms_metadata(
    cms: str,
    resource_id: str,
    patch: MetadataPatch,
) -> Dict[str, str]:
    """Endpoint stub that would delegate to CMS connectors."""

    # In a full deployment we would look up credentials and push to the CMS.
    return {
        "status": "queued",
        "cms": cms,
        "resource": resource_id,
        "fields": ", ".join(patch.dict(exclude_none=True).keys()),
    }
