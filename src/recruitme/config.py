"""Central configuration. Every value can be overridden with an environment variable,
so the same code runs on a laptop, in Docker, on Azure and on AWS without edits."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    llm_model: str = "llama3"
    embed_model: str = "nomic-embed-text"
    ollama_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.0
    data_dir: Path = Path("data")
    log_level: str = "INFO"

    @property
    def faiss_dir(self) -> Path:
        return self.data_dir / "faiss_index"

    @property
    def log_dir(self) -> Path:
        return self.data_dir / "logs"


def load_settings() -> Settings:
    """Build Settings from environment variables (see .env.example)."""
    return Settings(
        llm_model=os.getenv("LLM_MODEL", Settings.llm_model),
        embed_model=os.getenv("EMBED_MODEL", Settings.embed_model),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", Settings.ollama_base_url),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", Settings.llm_temperature)),
        data_dir=Path(os.getenv("DATA_DIR", str(Settings.data_dir))),
        log_level=os.getenv("LOG_LEVEL", Settings.log_level).upper(),
    )
