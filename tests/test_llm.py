import pytest

from recruitme import llm


def test_ask_wraps_errors(monkeypatch):
    class Boom:
        def invoke(self, _):
            raise ConnectionError("down")

    monkeypatch.setattr(llm, "get_llm", lambda: Boom())
    with pytest.raises(llm.LLMUnavailableError):
        llm.ask("hi")


def test_ask_returns_content(monkeypatch):
    class Fake:
        def invoke(self, _):
            return type("R", (), {"content": "hello"})()

    monkeypatch.setattr(llm, "get_llm", lambda: Fake())
    assert llm.ask("hi") == "hello"
