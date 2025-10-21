"""FastAPI application bootstrap."""
from __future__ import annotations

from fastapi import FastAPI

from .api.routes import api_router
from .core.config import settings

app = FastAPI(title=settings.project_name)
app.include_router(api_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple healthcheck endpoint for monitoring purposes."""

    return {"status": "ok"}
