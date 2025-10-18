from fastapi import FastAPI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Control Center Core API"
    version: str = "0.1.0"


settings = Settings()
app = FastAPI(title=settings.project_name, version=settings.version)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Simple readiness endpoint for compose healthchecks."""
    return {"status": "ok", "service": settings.project_name}


@app.get("/modules", tags=["modules"])
def modules() -> dict[str, list[str]]:
    return {
        "available": [
            "identity",
            "social-automation",
            "ai-content",
            "crm",
            "commerce",
            "intel",
        ]
    }
