from recruitme.matcher import match_candidate


def test_partial_match():
    score, matched, missing = match_candidate(["python", "sql"], ["python", "aws", "docker", "sql"])
    assert score == 50
    assert matched == ["python", "sql"]
    assert missing == ["aws", "docker"]


def test_full_match():
    assert match_candidate(["python"], ["python"])[0] == 100


def test_empty_jd_scores_zero():
    assert match_candidate(["python"], []) == (0, [], [])


def test_no_overlap():
    assert match_candidate(["sql"], ["aws"])[0] == 0
