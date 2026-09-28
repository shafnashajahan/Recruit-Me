from recruitme.cv_builder import build_cv_prompt, create_resume_pdf, extract_json


def test_extract_json_with_chatter_around_it():
    assert extract_json('Sure! {"summary": "hi"} hope it helps') == {"summary": "hi"}


def test_extract_json_invalid_returns_none():
    assert extract_json("no json here") is None
    assert extract_json("{not: valid}") is None
    assert extract_json("") is None


def test_prompt_contains_inputs():
    p = build_cv_prompt(name="Ann", email="a@b.c", phone="1", place="Kochi", skills="python",
                        projects="x", experience="y", job_description="JD TEXT")
    assert "Ann" in p and "JD TEXT" in p


def test_pdf_is_created_and_handles_special_characters():
    cv = {
        "summary": "R&D <engineer> & more",
        "skills": ["Python", {"name": "SQL"}],
        "experience": [{"role": "Dev", "company": "A&B", "duration": "2020-2022", "points": ["Did <x> & y"]}],
        "projects": [{"title": "Proj", "description": "", "points": ["p1"]}],
    }
    pdf = create_resume_pdf(cv, name="Ann", email="a@b.c", phone="1", place="Kochi",
                            describe_project=lambda t: f"About {t}")
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
