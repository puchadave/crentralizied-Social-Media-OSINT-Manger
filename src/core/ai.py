"""Integration helpers for OpenAI powered content generation."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable, Sequence

try:
    import openai
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore


@dataclass(slots=True)
class AIConfig:
    api_key: str
    model: str = "gpt-4o-mini"


class ContentGenerator:
    """Wrapper around the OpenAI Chat Completions API."""

    def __init__(self, config: AIConfig | None = None) -> None:
        api_key = config.api_key if config else os.getenv("OPENAI_API_KEY", "")
        model = config.model if config else os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.config = AIConfig(api_key=api_key, model=model)
        if openai and self.config.api_key:
            openai.api_key = self.config.api_key

    def is_available(self) -> bool:
        return bool(openai and self.config.api_key)

    def draft_post(self, brief: str, *, tone: str = "informative") -> str:
        if not self.is_available():
            return f"[offline] Draft for '{brief}' in tone '{tone}'."
        response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that writes social media content in German.",
                },
                {
                    "role": "user",
                    "content": f"Erstelle einen Social Media Post mit folgendem Briefing: {brief}\nTon: {tone}",
                },
            ],
        )
        return response["choices"][0]["message"]["content"].strip()

    def suggest_hashtags(self, keywords: Iterable[str]) -> list[str]:
        base = [f"#{keyword.replace(' ', '').lower()}" for keyword in keywords]
        return base[:5]

    def generate_video_storyboard(self, brief: str, *, duration: int = 30) -> str:
        """Create a SORA II compatible storyboard for short-form videos."""

        if not self.is_available():
            return (
                f"[offline] SORA II Storyboard für '{brief}' ({duration} Sekunden)\n"
                "1. Hook: Stimmung und Blickfang\n"
                "2. Hauptszene: Kernaussage mit B-Roll\n"
                "3. Call-to-Action: Markenbotschaft und CTA-Overlay"
            )
        response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein Creative Director, der für den SORA II Video Generator Szenenpläne, "
                        "Kameraeinstellungen und Voiceover-Stichpunkte erstellt."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Erstelle ein detailliertes Storyboard im JSON-Format für den SORA II KI Video Generator. "
                        f"Briefing: {brief}. Maximale Dauer: {duration} Sekunden. Enthalten sein sollen Szenenbeschreibungen, "
                        "visuelle Stichworte, Voiceover und Hinweise zu Musik/Soundeffekten."
                    ),
                },
            ],
        )
        return response["choices"][0]["message"]["content"].strip()

    def optimize_seo_plan(self, url: str, keywords: Sequence[str]) -> str:
        """Generate an optimization blueprint for a landing page."""

        keyword_text = ", ".join(keywords) or "SEO"
        if not self.is_available():
            lines = [
                f"Zielseite: {url or 'Landing Page'}",
                "\nTechnische Optimierung:",
                "- Core Web Vitals prüfen und Assets minimieren",
                "- Strukturierte Daten für Snippets ergänzen",
                "\nContent-Optimierung:",
                f"- Keywords priorisieren: {keyword_text}",
                "- FAQ-Sektion ergänzen und interne Verlinkung stärken",
                "\nOffpage & Monitoring:",
                "- Relevante Backlinks sichern und Alerts aktivieren",
            ]
            return "\n".join(lines)

        response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein SEO-Stratege, der klare Aktionspläne mit technischen, inhaltlichen und Offpage-Maßnahmen "
                        "liefert."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Erstelle einen deutschsprachigen SEO-Optimierungsplan für folgende URL: "
                        f"{url or 'Landing Page'}. Ziel-Keywords: {keyword_text}. "
                        "Strukturiere das Ergebnis mit Abschnitten für Technik, Inhalt, interne Verlinkung, Rich Snippets und "
                        "Offpage-Maßnahmen. Gib konkrete Schritte an."
                    ),
                },
            ],
        )
        return response["choices"][0]["message"]["content"].strip()

    def generate_meta_description(self, topic: str, keywords: Sequence[str], *, length: int = 160) -> str:
        """Compose a concise meta description for search results."""

        keyword_text = ", ".join(keywords) or "SEO"
        if not self.is_available():
            base = topic.strip() or "Landing Page"
            description = f"{base} – Optimiert für {keyword_text}. Jetzt informieren!"
            return description[:length]

        response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "Du schreibst prägnante Meta-Descriptions mit maximal 160 Zeichen.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Schreibe eine Meta-Description (max. {length} Zeichen) für {topic or 'eine Landing Page'}. "
                        f"Nutze die Keywords: {keyword_text}. Endung mit Call-to-Action."
                    ),
                },
            ],
        )
        return response["choices"][0]["message"]["content"].strip()


__all__ = ["AIConfig", "ContentGenerator"]
