"""Tailored CV generation: prompt -> LLM JSON -> PDF bytes."""
from __future__ import annotations

import io
import json
import logging
import re
from collections.abc import Callable
from typing import Any
from xml.sax.saxutils import escape

log = logging.getLogger(__name__)


def build_cv_prompt(*, name: str, email: str, phone: str, place: str,
                    skills: str, projects: str, experience: str, job_description: str) -> str:
    return f"""You are an expert CV writer.

Create a professional JSON CV tailored for this job description.
Do not invent employers, degrees or experience the user did not provide.

JOB DESCRIPTION:
{job_description}

USER DETAILS:
Name: {name}
Email: {email}
Phone: {phone}
Place: {place}
Skills: {skills}
Projects: {projects}
Experience: {experience}

Return ONLY valid JSON in this format:

{{
  "summary": "",
  "skills": [],
  "experience": [{{"role": "", "company": "", "duration": "", "points": []}}],
  "projects": [{{"title": "", "description": "", "points": []}}]
}}
"""


def extract_json(text: str) -> dict[str, Any] | None:
    """Pull the first {...} block out of an LLM reply. Returns None if it isn't valid JSON."""
    match = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        log.warning("LLM returned malformed JSON")
        return None
    return data if isinstance(data, dict) else None


def _p(text: object) -> str:
    """Escape text for ReportLab's mini-HTML so '&' or '<' in a CV can't crash PDF creation."""
    return escape(str(text or ""))


def create_resume_pdf(
    cv: dict[str, Any], *, name: str, email: str, phone: str, place: str,
    describe_project: Callable[[str], str] | None = None,
) -> bytes:
    """Render the CV dict to PDF and return the bytes (nothing is written to disk)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story: list = []

    def bullets(points: list) -> None:
        if points:
            story.append(ListFlowable(
                [ListItem(Paragraph(_p(x), styles["Normal"])) for x in points],
                bulletType="bullet"))

    story.append(Paragraph(f"<b>{_p(name)}</b>", styles["Title"]))
    story.append(Paragraph(f"{_p(phone)} | {_p(email)} | {_p(place)}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("PROFESSIONAL SUMMARY", styles["Heading2"]))
    story.append(Paragraph(_p(cv.get("summary")), styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("SKILLS", styles["Heading2"]))
    skills = [s.get("name") if isinstance(s, dict) else s for s in cv.get("skills", [])]
    story.append(Paragraph(" • ".join(_p(s) for s in skills) or "N/A", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("EXPERIENCE", styles["Heading2"]))
    for exp in cv.get("experience", []):
        heading = f"<b>{_p(exp.get('role'))} | {_p(exp.get('company'))}</b>"
        story.append(Paragraph(heading, styles["Heading3"]))
        story.append(Paragraph(f"<i>{_p(exp.get('duration'))}</i>", styles["Normal"]))
        bullets(exp.get("points", []))
        story.append(Spacer(1, 10))

    story.append(Paragraph("PROJECTS", styles["Heading2"]))
    for project in cv.get("projects", []):
        title = project.get("title", "")
        description = project.get("description", "")
        if not description and title and describe_project:
            description = describe_project(title)
        story.append(Paragraph(f"<b>{_p(title)}</b>", styles["Heading3"]))
        if description:
            story.append(Paragraph(f"<i>{_p(description)}</i>", styles["Normal"]))
        bullets(project.get("points", []))
        story.append(Spacer(1, 10))

    doc.build(story)  # NOTE: the original code never called build(), so no PDF was produced
    return buf.getvalue()
