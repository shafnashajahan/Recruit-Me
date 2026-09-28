"""Keyword-based skill extraction. Extend SKILLS to recognise more technologies."""
from __future__ import annotations

import re

SKILLS: tuple[str, ...] = (
    "python", "sql", "aws", "azure", "nlp", "machine learning", "deep learning",
    "genai", "langchain", "docker", "pytorch", "tensorflow", "streamlit", "power bi",
)

_PATTERNS = {s: re.compile(r"\b" + re.escape(s) + r"\b") for s in SKILLS}


def extract_skills(text: str) -> list[str]:
    """Return the sorted list of known skills that appear in `text` (case-insensitive)."""
    lowered = (text or "").lower()
    return sorted(s for s, pat in _PATTERNS.items() if pat.search(lowered))
