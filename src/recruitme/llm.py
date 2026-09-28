"""LLM access. Talks to an Ollama server whose address comes from OLLAMA_BASE_URL.

Keeping this in one place means moving to a hosted model later only changes this file."""
from __future__ import annotations

import logging
from functools import lru_cache

from recruitme.config import load_settings

log = logging.getLogger(__name__)


class LLMUnavailableError(RuntimeError):
    """Raised when the LLM server cannot be reached or returns an error."""


@lru_cache(maxsize=1)
def get_llm():
    from langchain_ollama import ChatOllama

    s = load_settings()
    return ChatOllama(model=s.llm_model, base_url=s.ollama_base_url, temperature=s.llm_temperature)


def ask(prompt: str) -> str:
    """Send a prompt, return the text answer. Raises LLMUnavailableError on failure."""
    try:
        return get_llm().invoke(prompt).content
    except Exception as exc:  # network errors, model not pulled, etc.
        log.exception("LLM call failed")
        raise LLMUnavailableError(
            f"Could not reach the LLM at {load_settings().ollama_base_url}. "
            "Start Ollama (`ollama serve`) or set OLLAMA_BASE_URL."
        ) from exc
