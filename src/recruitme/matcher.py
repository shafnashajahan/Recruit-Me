"""Score how well a candidate's skills cover the job description's skills."""
from __future__ import annotations

from collections.abc import Iterable


def match_candidate(
    resume_skills: Iterable[str], jd_skills: Iterable[str]
) -> tuple[int, list[str], list[str]]:
    """Return (score 0-100, matched skills, missing skills). Lists are sorted."""
    resume, jd = set(resume_skills), set(jd_skills)
    matched = sorted(resume & jd)
    missing = sorted(jd - resume)
    score = int(len(matched) / len(jd) * 100) if jd else 0
    return score, matched, missing
