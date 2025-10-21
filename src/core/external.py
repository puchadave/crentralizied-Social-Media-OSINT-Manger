"""Real-time external reach analysis and optimization helpers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import cos, sin
from typing import Sequence

from .ai import ContentGenerator
from .analytics import TimeSeriesPoint


@dataclass(slots=True)
class ExternalMetric:
    """Snapshot of a network's current external performance."""

    network: str
    share_of_voice: float
    sentiment: float
    mentions_per_hour: float
    trend_percentage: float


@dataclass(slots=True)
class ExternalOptimization:
    """Recommended action to increase off-site reach."""

    network: str
    action: str
    expected_gain: float
    hashtags: list[str]


class ExternalAnalysisService:
    """Provide simulated real-time external monitoring data."""

    def __init__(self, generator: ContentGenerator) -> None:
        self._generator = generator
        self._boot = datetime.utcnow()
        self._networks: list[str] = [
            "Facebook",
            "Instagram",
            "LinkedIn",
            "YouTube",
            "TikTok",
            "X",
            "Reddit",
        ]
        self._baseline_share: dict[str, float] = {
            "Facebook": 24,
            "Instagram": 20,
            "LinkedIn": 12,
            "YouTube": 18,
            "TikTok": 14,
            "X": 7,
            "Reddit": 5,
        }
        self._topic_pool: dict[str, list[str]] = {
            "Facebook": ["Community Story", "Live Q&A", "Event-Recap"],
            "Instagram": ["Reel-Serie", "Behind-the-Scenes", "Creator Spotlight"],
            "LinkedIn": ["Thought Leadership", "Employer Branding", "Produktupdate"],
            "YouTube": ["How-To Video", "Produkt Demo", "Case Study"],
            "TikTok": ["Trend Sound", "Challenge", "Creator Duet"],
            "X": ["Realtime Update", "Thread", "Spaces Talk"],
            "Reddit": ["AMA", "Deep Dive", "Community Poll"],
        }

    def realtime_metrics(self) -> list[ExternalMetric]:
        """Return the latest external share-of-voice snapshot."""

        now = datetime.utcnow()
        elapsed_minutes = (now - self._boot).total_seconds() / 60
        raw_scores: dict[str, float] = {}
        for index, network in enumerate(self._networks):
            baseline = self._baseline_share[network]
            oscillation = 4.5 * sin(elapsed_minutes / 3 + index / 2)
            campaign_boost = 2.3 * cos(elapsed_minutes / 5 + index)
            raw = max(1.0, baseline + oscillation + campaign_boost)
            raw_scores[network] = raw

        total = sum(raw_scores.values()) or 1.0
        metrics: list[ExternalMetric] = []
        for index, network in enumerate(self._networks):
            share = raw_scores[network] / total * 100
            sentiment = 58 + 18 * sin(elapsed_minutes / 4 + index / 3)
            mentions = 160 + 45 * cos(elapsed_minutes / 6 + index / 4)
            trend = 2.2 * cos(elapsed_minutes / 3.5 + index / 2.3)
            metrics.append(
                ExternalMetric(
                    network=network,
                    share_of_voice=round(share, 2),
                    sentiment=round(max(10.0, min(95.0, sentiment)), 1),
                    mentions_per_hour=round(max(20.0, mentions), 1),
                    trend_percentage=round(trend, 2),
                )
            )
        return metrics

    def share_of_voice_timeseries(self, minutes: int = 90, interval: int = 5) -> dict[str, list[TimeSeriesPoint]]:
        """Return rolling share-of-voice time series for each network."""

        if minutes <= 0 or interval <= 0:
            return {network: [] for network in self._networks}

        now = datetime.utcnow()
        series: dict[str, list[TimeSeriesPoint]] = {network: [] for network in self._networks}
        for minutes_ago in range(minutes, -1, -interval):
            timestamp = now - timedelta(minutes=minutes_ago)
            elapsed = (timestamp - self._boot).total_seconds() / 60
            raw_scores: dict[str, float] = {}
            for index, network in enumerate(self._networks):
                baseline = self._baseline_share[network]
                oscillation = 4.5 * sin(elapsed / 3 + index / 2)
                campaign_boost = 2.3 * cos(elapsed / 5 + index)
                raw_scores[network] = max(1.0, baseline + oscillation + campaign_boost)

            total = sum(raw_scores.values()) or 1.0
            for network in self._networks:
                share = raw_scores[network] / total * 100
                series[network].append(TimeSeriesPoint(timestamp=timestamp, value=round(share, 2)))
        return series

    def optimization_recommendations(
        self, metrics: Sequence[ExternalMetric] | None = None
    ) -> list[ExternalOptimization]:
        """Suggest real-time actions to maximise external reach."""

        snapshot = list(metrics) if metrics is not None else self.realtime_metrics()
        if not snapshot:
            return []

        elapsed = (datetime.utcnow() - self._boot).total_seconds() / 10
        ordered = sorted(snapshot, key=lambda metric: (metric.trend_percentage, metric.share_of_voice))
        recommendations: list[ExternalOptimization] = []
        for metric in ordered:
            topics = self._topic_pool.get(metric.network, ["Campaign"])
            topic_index = int(abs(elapsed + metric.share_of_voice) // 3) % len(topics)
            focus_topic = topics[topic_index]
            sentiment_gap = max(0.0, 75.0 - metric.sentiment)
            base_gain = 6.0 + sentiment_gap / 12 + abs(metric.trend_percentage) * 1.4
            if metric.trend_percentage < 0:
                action = (
                    f"Boost {metric.network} mit einer {focus_topic} Serie und Paid Reach in der Peak-Zeit."
                )
            else:
                action = (
                    f"Skaliere das Momentum auf {metric.network} – erweitere die {focus_topic} Inhalte cross-channel."
                )
            hashtags = self._generator.suggest_hashtags(
                [metric.network, focus_topic, "Reichweite", "Growth"]
            )
            recommendations.append(
                ExternalOptimization(
                    network=metric.network,
                    action=action,
                    expected_gain=round(min(25.0, base_gain), 1),
                    hashtags=hashtags,
                )
            )

        top_performer = max(snapshot, key=lambda metric: metric.share_of_voice)
        topics = self._topic_pool.get(top_performer.network, ["Campaign"])
        topic = topics[int(elapsed) % len(topics)]
        hashtags = self._generator.suggest_hashtags([
            top_performer.network,
            topic,
            "Lookalike",
        ])
        recommendations.insert(
            0,
            ExternalOptimization(
                network=top_performer.network,
                action=(
                    f"Nutze das Momentum auf {top_performer.network}: starte ein Lookalike-Retargeting mit {topic} Fokus."
                ),
                expected_gain=round(min(30.0, 9.5 + top_performer.trend_percentage * 1.8), 1),
                hashtags=hashtags,
            ),
        )

        unique: dict[str, ExternalOptimization] = {}
        for recommendation in recommendations:
            if recommendation.network not in unique:
                unique[recommendation.network] = recommendation
        return list(unique.values())[:4]


__all__ = [
    "ExternalMetric",
    "ExternalOptimization",
    "ExternalAnalysisService",
]

