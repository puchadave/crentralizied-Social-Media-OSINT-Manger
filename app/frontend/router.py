"""Router für die einseitige Web-GUI."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["web"], include_in_schema=False)

_dashboard_path = Path(__file__).with_name("dashboard.html")
_dashboard_html = _dashboard_path.read_text(encoding="utf-8")


@router.get("/", response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    """Liefer die zentrale Dashboard-Oberfläche."""

    return HTMLResponse(content=_dashboard_html)
