"""Real-time SEO analytics and optimization helpers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import cos, sin
from typing import Sequence

from .ai import ContentGenerator


@dataclass(slots=True)
class SEOMetric:
    name: str
    value: float
    unit: str
    trend_percentage: float


@dataclass(slots=True)
class SEOPlan:
    plan_text: str
    meta_description: str
    recommended_keywords: list[str]
    structured_data: str
    projected_gain: float


class SEOOptimizationService:
    """Provide synthetic real-time SEO data and AI-assisted improvements."""

    def __init__(self, generator: ContentGenerator) -> None:
        self._generator = generator
        self._created_at = datetime.utcnow()

    def realtime_metrics(self) -> list[SEOMetric]:
        now = datetime.utcnow()
        elapsed_minutes = (now - self._created_at).total_seconds() / 60
        visibility = 82 + 3.5 * sin(elapsed_minutes / 2)
        serp = 5 + 1.2 * cos(elapsed_minutes / 4)
        page_speed = 2.1 + 0.25 * cos(elapsed_minutes / 6)
        seo_score = 78 + 4 * sin(elapsed_minutes / 3)

        return [
            SEOMetric(
                name="SEO Sichtbarkeit",
                value=max(60.0, visibility),
                unit="Index",
                trend_percentage=1.1 * cos(elapsed_minutes / 2),
            ),
            SEOMetric(
                name="Durchschn. SERP-Position",
                value=max(1.0, serp),
                unit="Platz",
                trend_percentage=-1.6 * sin(elapsed_minutes / 4),
            ),
            SEOMetric(
                name="PageSpeed",
                value=max(1.2, page_speed),
                unit="Sek.",
                trend_percentage=-0.8 * sin(elapsed_minutes / 6),
            ),
            SEOMetric(
                name="SEO Health Score",
                value=max(50.0, seo_score),
                unit="Score",
                trend_percentage=1.4 * cos(elapsed_minutes / 3),
            ),
        ]

    def keyword_opportunities(self, focus_keywords: Sequence[str] | None = None) -> list[str]:
        normalized = [keyword.strip().lower() for keyword in (focus_keywords or []) if keyword.strip()]
        if not normalized:
            normalized = ["seo", "content marketing"]
        base = set(normalized)
        suggestions = {f"{keyword} trends" for keyword in normalized}
        suggestions.update(f"{keyword} automation" for keyword in normalized)
        suggestions.update(f"{keyword} strategie" for keyword in normalized)
        ordered = sorted(base.union(suggestions))
        return ordered[:8]

    def projected_gain(self, keywords: Sequence[str] | None = None) -> float:
        keyword_count = len([kw for kw in (keywords or []) if kw.strip()])
        baseline = 9.5 + keyword_count * 1.3
        oscillation = 1.8 * sin((datetime.utcnow() - self._created_at).total_seconds() / 300)
        return round(baseline + oscillation, 1)

    def optimization_plan(self, url: str, keywords: Sequence[str]) -> SEOPlan:
        keyword_list = [kw.strip() for kw in keywords if kw.strip()]
        if not keyword_list:
            keyword_list = ["seo automation", "ki marketing"]

        plan_text = self._generator.optimize_seo_plan(url, keyword_list)
        meta_description = self._generator.generate_meta_description(url or "Landing Page", keyword_list)
        recommended = self.keyword_opportunities(keyword_list)
        structured_data = self._build_structured_data(url, keyword_list)
        projected_gain = self.projected_gain(keyword_list)

        return SEOPlan(
            plan_text=plan_text,
            meta_description=meta_description,
            recommended_keywords=recommended,
            structured_data=structured_data,
            projected_gain=projected_gain,
        )

    def _build_structured_data(self, url: str, keywords: Sequence[str]) -> str:
        primary = keywords[0] if keywords else "SEO"
        keywords_csv = ", ".join(keywords)
        return (
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "WebSite",\n'
            f'  "url": "{url or "https://example.com"}",\n'
            f'  "name": "{primary.title()} Kampagne",\n'
            '  "potentialAction": {{\n'
            '    "@type": "SearchAction",\n'
            f'    "target": "{url or "https://example.com"}/?q={{search_term_string}}",\n'
            '    "query-input": "required name=search_term_string"\n'
            '  }},\n'
            f'  "keywords": "{keywords_csv}"\n'
            '}\n'
        )


__all__ = [
    "SEOMetric",
    "SEOPlan",
    "SEOOptimizationService",
]
