"""Aggregate API routers for the FastAPI application."""
from __future__ import annotations

from fastapi import APIRouter

from .v1 import content, monitoring, scheduling


api_router = APIRouter()
api_router.include_router(content.router, prefix="/v1")
api_router.include_router(scheduling.router, prefix="/v1")
api_router.include_router(monitoring.router, prefix="/v1")
