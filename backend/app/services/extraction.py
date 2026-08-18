from typing import Optional
import os


def extract_text_from_pdf(path: str) -> str:
    """Extract PDF text with PyMuPDF, falling back to PyPDF2 when needed."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    # PyMuPDF handles a wider range of PDFs than PyPDF2, including many PDFs
    # produced by office tools. Keep imports lazy so importing this module has
    # no dependency side effects.
    try:
        import pymupdf

        with pymupdf.open(path) as document:
            text = "\n".join(page.get_text("text") for page in document)
        if text.strip():
            return text
    except Exception:
        # Fall through to the existing parser for compatibility with PDFs that
        # PyMuPDF cannot open, or environments where it is unavailable.
        pass

    try:
        from PyPDF2 import PdfReader
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("PyMuPDF or PyPDF2 is required for PDF extraction but neither is installed") from exc

    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def try_extract(path: str) -> str:
    """Wrapper for future OCR fallback; currently just calls extract_text_from_pdf."""
    return extract_text_from_pdf(path)
