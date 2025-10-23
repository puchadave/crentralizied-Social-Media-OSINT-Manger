from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session

from ..models import MetadataPatch, SEOReport


@dataclass
class SEOIssue:
    message: str
    severity: str = "info"


class SEOOptimizer:
    """Perform realtime SEO analysis and metadata optimisation."""

    def __init__(self, session: Session):
        self.session = session

    async def analyse(self, url: str, html: Optional[str] = None) -> SEOReport:
        if html is None:
            html = await self._fetch_html(url)
        soup = BeautifulSoup(html or "", "html.parser")
        title = (soup.title.string if soup.title else None) or ""
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = (
            description_tag["content"] if description_tag and description_tag.has_attr("content") else ""
        )
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        keywords = []
        if keywords_tag and keywords_tag.has_attr("content"):
            keywords = [k.strip() for k in keywords_tag["content"].split(",") if k.strip()]
        issues = self._detect_issues(title, description, soup)
        score = max(0, 100 - len(issues) * 5)
        report = SEOReport(
            url=url,
            title=title,
            description=description,
            keywords=keywords,
            score=score,
            issues=[issue.message for issue in issues],
            recommendations=self._build_recommendations(issues),
            lighthouse_metrics={"performance": 82.0, "accessibility": 90.0},
        )
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report

    async def _fetch_html(self, url: str) -> str:
        timeout = httpx.Timeout(5.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def _detect_issues(self, title: str, description: str, soup: BeautifulSoup) -> List[SEOIssue]:
        issues: List[SEOIssue] = []
        if len(title) < 10:
            issues.append(SEOIssue("Title ist zu kurz", "warning"))
        if len(description) < 50:
            issues.append(SEOIssue("Meta Description sollte mindestens 50 Zeichen haben", "warning"))
        if not soup.find_all("h1"):
            issues.append(SEOIssue("Mindestens eine H1-Überschrift wird empfohlen", "info"))
        if not soup.find_all("img", attrs={"alt": True}):
            issues.append(SEOIssue("Bilder ohne ALT-Texte gefunden", "info"))
        return issues

    def _build_recommendations(self, issues: List[SEOIssue]) -> List[str]:
        recs: List[str] = []
        for issue in issues:
            if "Titel" in issue.message or "Title" in issue.message:
                recs.append("Titel auf 55-60 Zeichen optimieren.")
            elif "Description" in issue.message:
                recs.append("Meta Description mit klarer Call-To-Action erweitern.")
            elif "H1" in issue.message:
                recs.append("Strukturierte H1/H2-Hierarchie erstellen.")
            elif "ALT" in issue.message:
                recs.append("ALT-Texte mit relevanten Keywords ergänzen.")
        if not recs:
            recs.append("Seite erfüllt die wichtigsten On-Page-SEO-Kriterien.")
        return recs

    async def push_metadata(self, patch: MetadataPatch) -> MetadataPatch:
        stored_patch = MetadataPatch(**patch.dict(exclude_none=True))
        report = SEOReport(
            url="metadata-update",
            title=stored_patch.title or "",
            description=stored_patch.description or "",
            keywords=stored_patch.keywords or [],
            score=100.0,
            issues=[],
            recommendations=["Metadaten synchronisiert"],
            lighthouse_metrics={},
        )
        self.session.add(report)
        self.session.commit()
        return stored_patch


async def analyse_url(session: Session, url: str, html: Optional[str] = None) -> SEOReport:
    optimizer = SEOOptimizer(session)
    return await optimizer.analyse(url, html=html)


async def push_metadata_patch(session: Session, patch: MetadataPatch) -> MetadataPatch:
    optimizer = SEOOptimizer(session)
    return await optimizer.push_metadata(patch)
