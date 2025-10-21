"""Service responsible for orchestrating LLM backed content generation."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx

from ..core.config import Settings
from ..models.content import (
    ContentGenerationMetadata,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentPiece,
    ContentSection,
)
from ..utils.time import utc_now

LOGGER = logging.getLogger(__name__)
HASHTAG_PATTERN = re.compile(r"(?i)(?<!&)#([\wäöüß]+)")


@dataclass
class _ProviderResult:
    content: str
    raw_response: dict[str, Any]


class ContentGeneratorService:
    """Generate structured social media content via OpenAI or deterministic fallbacks."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate_content(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """Generate content for the requested topic and platform."""

        prompt = self._build_prompt(request)

        if not self._settings.openai_api_key:
            LOGGER.info("OPENAI_API_KEY missing – using deterministic fallback generator")
            content = self._fallback_content(request)
            metadata = ContentGenerationMetadata(
                model="fallback-template",
                prompt=prompt,
                used_fallback=True,
            )
            return ContentGenerationResponse(request=request, content=content, metadata=metadata)

        try:
            provider_result = await self._call_openai(prompt)
            content_piece = self._structure_model_output(provider_result.content, request)
            metadata = ContentGenerationMetadata(
                model=self._settings.openai_model,
                prompt=prompt,
                raw_response=provider_result.raw_response,
            )
            return ContentGenerationResponse(
                request=request,
                content=content_piece,
                metadata=metadata,
            )
        except Exception as exc:  # pragma: no cover - protective fallback
            LOGGER.warning("Falling back to deterministic generator due to error: %s", exc)
            content = self._fallback_content(request)
            metadata = ContentGenerationMetadata(
                model=self._settings.openai_model,
                prompt=prompt,
                used_fallback=True,
            )
            return ContentGenerationResponse(request=request, content=content, metadata=metadata)

    async def _call_openai(self, prompt: str) -> _ProviderResult:
        """Call the OpenAI Chat Completion endpoint with the constructed prompt."""

        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
        }
        payload = {
            "model": self._settings.openai_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Du bist ein professioneller Social-Media-Strategist, der datengetrieben "
                        "arbeite und strukturierte Ergebnisse zurückliefert."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.7,
            "top_p": 0.9,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
            response = await client.post(
                f"{self._settings.openai_api_base}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        try:
            message_content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError("Malformed response from OpenAI") from exc

        return _ProviderResult(content=message_content, raw_response=data)

    def _build_prompt(self, request: ContentGenerationRequest) -> str:
        """Craft a structured prompt for the LLM."""

        sections = [
            f"Thema: {request.topic}",
            f"Plattform: {request.platform}",
            f"Sprache: {request.language}",
            f"Tonalität: {request.tone}",
            f"Format: {request.format}",
        ]
        if request.audience:
            sections.append(f"Zielgruppe: {request.audience}")

        instructions = (
            "Erstelle einen strukturierten Output im JSON-Format mit den Feldern 'title', "
            "'summary', 'body', 'hashtags' (als Liste) und optional 'call_to_action'. "
            "Für Newsletter füge ein Feld 'sections' mit Objekten bestehend aus 'heading' "
            "und 'body' hinzu."
        )
        sections.append(instructions)
        return "\n".join(sections)

    def _structure_model_output(
        self, message: str, request: ContentGenerationRequest
    ) -> ContentPiece:
        """Convert the model output into the :class:`ContentPiece` data structure."""

        text = message.strip()
        hashtags = sorted({f"#{match}" for match in HASHTAG_PATTERN.findall(text)})

        if text.startswith("{"):
            # Attempt to parse JSON like output
            import json

            try:
                payload = json.loads(text)
                sections = [
                    ContentSection(heading=item.get("heading"), body=item.get("body", ""))
                    for item in payload.get("sections", [])
                ]
                return ContentPiece(
                    title=payload.get("title"),
                    summary=payload.get("summary"),
                    body=payload.get("body", ""),
                    hashtags=payload.get("hashtags", hashtags),
                    call_to_action=payload.get("call_to_action"),
                    sections=[section for section in sections if section.body],
                )
            except (ValueError, TypeError):
                LOGGER.debug("Failed to parse JSON response, falling back to heuristic parsing")

        if request.format == "newsletter":
            sections = [
                ContentSection(heading=None, body=paragraph.strip())
                for paragraph in text.split("\n\n")
            ]
        else:
            sections = []

        summary = None
        sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
        if sentences:
            summary = sentences[0] + "."

        call_to_action = None
        for sentence in sentences[::-1]:
            if sentence.endswith("?"):
                call_to_action = sentence + "."
                break

        return ContentPiece(
            title=None,
            summary=summary,
            body=text,
            hashtags=list(hashtags),
            call_to_action=call_to_action,
            sections=sections,
        )

    def _fallback_content(self, request: ContentGenerationRequest) -> ContentPiece:
        """Generate deterministic template based content for offline/local usage."""

        timestamp = utc_now().strftime("%Y-%m-%d")
        intro = (
            f"Aktuelles Highlight zum Thema {request.topic} auf {request.platform}. "
            f"{request.tone.capitalize()} Insights für {request.audience or 'deine Community'} "
            f"({timestamp})."
        )
        body_parts = [intro]

        if request.format == "newsletter":
            sections = [
                ContentSection(
                    heading="Einordnung",
                    body=(
                        f"Warum {request.topic} für {request.platform} aktuell relevant ist und welche "
                        "Chancen sich daraus ergeben."
                    ),
                ),
                ContentSection(
                    heading="Zahlen & Fakten",
                    body=(
                        "Kurze Sammlung verlässlicher Kennzahlen, Studien oder Zitate, die das Thema "
                        "untermauern."
                    ),
                ),
                ContentSection(
                    heading="Nächste Schritte",
                    body=(
                        "Konkrete Empfehlungen, wie Leser:innen mit den Informationen arbeiten können "
                        "und welche Tools dabei helfen."
                    ),
                ),
            ]
            body_parts.extend(section.body for section in sections)
        elif request.format == "thread":
            sections = [
                ContentSection(
                    heading=None,
                    body=f"1/ Starte mit einer provokanten Frage zu {request.topic}.",
                ),
                ContentSection(
                    heading=None,
                    body="2/ Teile einen spannenden Datenpunkt oder ein Beispiel.",
                ),
                ContentSection(
                    heading=None,
                    body="3/ Nenne eine Handlungsempfehlung und lade zur Diskussion ein.",
                ),
            ]
            body_parts.extend(section.body for section in sections)
        else:
            sections = []
            body_parts.append(
                "Teile eine kurze Erfolgsgeschichte oder ein aktuelles Projekt, das das Thema "
                "anschaulich macht."
            )
            body_parts.append("Schließe mit einer Frage an die Community, um Engagement anzuregen.")

        hashtags = [
            f"#{request.topic.lower().replace(' ', '')[:20]}",
            f"#{request.platform.lower()}",
        ]

        call_to_action = "Welche Erfahrungen habt ihr mit dem Thema gemacht?"
        body = "\n\n".join(body_parts)
        return ContentPiece(
            title=f"Deep-Dive: {request.topic}",
            summary=f"Wesentliche Insights zu {request.topic} für {request.platform}.",
            body=body,
            hashtags=hashtags,
            call_to_action=call_to_action,
            sections=sections,
        )


async def generate_content_sync(service: ContentGeneratorService, request: ContentGenerationRequest) -> ContentGenerationResponse:
    """Compatibility helper allowing synchronous contexts to call the async API."""

    return await service.generate_content(request)
