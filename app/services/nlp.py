from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, List, Tuple

POSITIVE_WORDS = {
    "awesome",
    "amazing",
    "stark",
    "gut",
    "great",
    "love",
    "fantastic",
    "erfolgreich",
    "win",
    "progress",
}
NEGATIVE_WORDS = {
    "schlecht",
    "bad",
    "fail",
    "down",
    "verlust",
    "kritik",
    "angry",
    "problem",
    "error",
}
STOPWORDS = {"und", "oder", "aber", "the", "is", "are", "ein", "eine"}
TAG_PATTERN = re.compile(r"[#@]?([\w-]{3,})")


def normalise_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_tags(text: str) -> List[str]:
    candidates = [match.group(1).lower() for match in TAG_PATTERN.finditer(text)]
    keywords = [c for c in candidates if c not in STOPWORDS]
    return list(dict.fromkeys(keywords))


def sentiment_score(text: str) -> float:
    words = re.findall(r"[\w-]+", text.lower())
    if not words:
        return 0.0
    positives = sum(1 for word in words if word in POSITIVE_WORDS)
    negatives = sum(1 for word in words if word in NEGATIVE_WORDS)
    score = positives - negatives
    return max(-1.0, min(1.0, score / math.sqrt(len(words))))


def keyword_frequencies(texts: Iterable[str]) -> List[Tuple[str, int]]:
    counter: Counter[str] = Counter()
    for text in texts:
        for tag in extract_tags(text):
            counter[tag] += 1
    return counter.most_common()
