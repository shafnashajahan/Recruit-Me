"""FAISS vector store for job descriptions and resumes (needs Ollama embeddings)."""
from __future__ import annotations

import logging

from recruitme.config import load_settings

log = logging.getLogger(__name__)


def _embeddings():
    from langchain_ollama import OllamaEmbeddings

    s = load_settings()
    return OllamaEmbeddings(model=s.embed_model, base_url=s.ollama_base_url)


def create_vector_store(documents: list[str]):
    """Embed `documents` and save the index under DATA_DIR/faiss_index."""
    from langchain_community.vectorstores import FAISS

    settings = load_settings()
    settings.faiss_dir.mkdir(parents=True, exist_ok=True)
    db = FAISS.from_texts(documents, _embeddings())
    db.save_local(str(settings.faiss_dir))
    log.info("Saved FAISS index with %d documents", len(documents))
    return db


def load_retriever(k: int = 5):
    """Load the saved index. Only load indexes this app created: FAISS uses pickle."""
    from langchain_community.vectorstores import FAISS

    db = FAISS.load_local(
        str(load_settings().faiss_dir), _embeddings(), allow_dangerous_deserialization=True
    )
    return db.as_retriever(search_kwargs={"k": k})
