"""Generate interview questions for a candidate."""
from __future__ import annotations

from collections.abc import Iterable

from recruitme.llm import ask


def build_prompt(resume_text: str, job_description: str, matched_skills: Iterable[str]) -> str:
    return f"""You are a senior technical interviewer.

Resume:
{resume_text}

Job Description:
{job_description}

Matched Skills:
{', '.join(matched_skills)}

Generate:
1. Technical questions
2. Project questions
3. Behavioral questions.
"""


def generate_questions(resume_text: str, job_description: str, matched_skills: Iterable[str]) -> str:
    return ask(build_prompt(resume_text, job_description, matched_skills))
