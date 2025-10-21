"""Routes for AI based content generation."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ...dependencies import get_content_generator_service
from ...models.content import ContentGenerationRequest, ContentGenerationResponse
from ...services.content_generator import ContentGeneratorService

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    payload: ContentGenerationRequest,
    service: ContentGeneratorService = Depends(get_content_generator_service),
) -> ContentGenerationResponse:
    """Generate social media or newsletter content via OpenAI."""

    return await service.generate_content(payload)
