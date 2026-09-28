from recruitme.skills import extract_skills


def test_finds_known_skills_case_insensitive():
    assert extract_skills("Built APIs in Python with Docker and AWS") == ["aws", "docker", "python"]


def test_multiword_skill():
    assert "machine learning" in extract_skills("Experienced in Machine Learning")


def test_no_partial_word_match():
    assert extract_skills("pythonic sqlite") == []


def test_empty_and_none():
    assert extract_skills("") == []
    assert extract_skills(None) == []
