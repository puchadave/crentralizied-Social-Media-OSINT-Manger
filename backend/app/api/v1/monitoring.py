"""Routes for OSINT monitoring and analytics."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ...dependencies import get_osint_service
from ...models.monitoring import (
    InteractionIngestRequest,
    InteractionSummary,
    NetworkGraph,
)
from ...services.osint import OsintService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/interactions", response_model=InteractionSummary, status_code=status.HTTP_201_CREATED)
def ingest_interactions(
    payload: InteractionIngestRequest,
    service: OsintService = Depends(get_osint_service),
) -> InteractionSummary:
    """Store monitored interactions for a post and return the aggregated summary."""

    return service.ingest(payload)


@router.get("/posts/{post_id}/summary", response_model=InteractionSummary)
def get_post_summary(
    post_id: str,
    service: OsintService = Depends(get_osint_service),
) -> InteractionSummary:
    """Return summary statistics for a monitored post."""

    summary = service.get_summary(post_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return summary


@router.get("/posts/{post_id}/network", response_model=NetworkGraph)
def get_post_network(
    post_id: str,
    service: OsintService = Depends(get_osint_service),
) -> NetworkGraph:
    """Return a network graph showing interactions around the monitored post."""

    graph = service.get_network_graph(post_id)
    if not graph:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return graph
