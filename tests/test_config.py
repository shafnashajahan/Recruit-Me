from recruitme.config import load_settings


def test_defaults(monkeypatch):
    for k in ("LLM_MODEL", "OLLAMA_BASE_URL", "DATA_DIR"):
        monkeypatch.delenv(k, raising=False)
    s = load_settings()
    assert s.llm_model == "llama3"
    assert s.ollama_base_url == "http://localhost:11434"


def test_env_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://10.0.0.5:11434")
    monkeypatch.setenv("DATA_DIR", "/tmp/x")
    s = load_settings()
    assert s.ollama_base_url == "http://10.0.0.5:11434"
    assert str(s.faiss_dir) == "/tmp/x/faiss_index"
