"""Streamlit UI. Run with:  streamlit run app/streamlit_app.py"""
import tempfile
from pathlib import Path

import streamlit as st

from recruitme.cv_builder import build_cv_prompt, create_resume_pdf, extract_json
from recruitme.interviewer import generate_questions
from recruitme.llm import LLMUnavailableError, ask
from recruitme.logging_setup import setup_logging
from recruitme.matcher import match_candidate
from recruitme.parser import extract_text
from recruitme.skills import extract_skills
from recruitme.vector_store import create_vector_store

setup_logging()
st.set_page_config(page_title="RecruitMe - AI Career Assistant", layout="wide")
st.title("RecruitMe - AI Career Assistant")
st.caption("Recruiter + CV Builder in one system")

mode = st.radio("Select Mode", ["Recruiter", "CV Builder"], horizontal=True)
st.divider()


def recruiter_mode() -> None:
    col1, col2 = st.columns(2)
    resumes = col1.file_uploader("Upload Resumes", type=["pdf"], accept_multiple_files=True)
    job_description = col2.text_area("Paste Job Description", height=200)
    use_llm = st.checkbox("Generate interview questions (needs Ollama)", value=True)

    if not st.button("Analyze Candidates"):
        return
    if not resumes:
        st.error("Upload at least one resume")
        return
    if not job_description.strip():
        st.error("Paste the job description")
        return

    jd_skills = extract_skills(job_description)
    documents = [job_description]

    for file in resumes:
        # Resumes contain personal data: parse from a temp file and never keep it.
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = Path(tmp) / "resume.pdf"
            pdf_path.write_bytes(file.getbuffer())
            try:
                text = extract_text(pdf_path)
            except Exception:
                st.error(f"Could not read {file.name}")
                continue

        skills = extract_skills(text)
        score, matched, missing = match_candidate(skills, jd_skills)
        documents.append(text)

        with st.container(border=True):
            st.subheader(file.name)
            st.metric("Match Score", f"{score}%")
            a, b = st.columns(2)
            a.markdown("**Matched Skills**")
            a.write(", ".join(matched) or "None")
            b.markdown("**Missing Skills**")
            b.write(", ".join(missing) or "None")
            if use_llm:
                st.markdown("**Interview Questions**")
                try:
                    st.write(generate_questions(text, job_description, matched))
                except LLMUnavailableError as exc:
                    st.warning(str(exc))

    try:
        create_vector_store(documents)
    except Exception:
        st.info("Vector index skipped (embedding model not reachable).")
    st.success("Analysis complete")


def cv_builder_mode() -> None:
    st.subheader("AI Job-Specific CV Generator")
    col1, col2 = st.columns(2)
    name = col1.text_input("Full Name")
    email = col1.text_input("Email")
    phone = col1.text_input("Phone")
    place = col1.text_input("Location")
    skills = col1.text_area("Skills (comma separated)")
    projects = col1.text_area("Projects (comma separated)")
    experience = col2.text_area("Experience (short description)")
    job_description = col2.text_area("Paste Target Job Description", height=200)

    if not st.button("Generate CV"):
        return
    if not name or not job_description:
        st.error("Name and Job Description are required")
        return

    prompt = build_cv_prompt(name=name, email=email, phone=phone, place=place, skills=skills,
                             projects=projects, experience=experience, job_description=job_description)
    try:
        cv = extract_json(ask(prompt))
    except LLMUnavailableError as exc:
        st.error(str(exc))
        return
    if cv is None:
        st.error("The model did not return valid JSON. Please try again.")
        return

    def describe(title: str) -> str:
        return ask(
            f"Write a professional 1-2 sentence ATS-friendly resume description for the project: {title}"
        ).strip()

    pdf_bytes = create_resume_pdf(cv, name=name, email=email, phone=phone, place=place,
                                  describe_project=describe)
    st.download_button("Download CV PDF", pdf_bytes,
                       file_name=f"{name.replace(' ', '_')}_CV.pdf", mime="application/pdf")
    st.success("CV generated successfully")


recruiter_mode() if mode == "Recruiter" else cv_builder_mode()
