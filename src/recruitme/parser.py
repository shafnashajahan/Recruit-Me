"""PDF text extraction."""
from __future__ import annotations

from pathlib import Path


def extract_text(pdf_path: str | Path) -> str:
    """Return all text from a PDF. Raises FileNotFoundError / RuntimeError on bad input."""
    import fitz  # PyMuPDF, imported lazily so tests/CI that don't need PDFs stay light

    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")
    with fitz.open(path) as doc:
        return "".join(page.get_text() for page in doc)
