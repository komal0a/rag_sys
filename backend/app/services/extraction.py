from typing import Optional
import os


def extract_text_from_pdf(path: str) -> str:
    """Extract text from a PDF file using PyPDF2.

    Import PyPDF2 lazily so test environments without the package can still import the module.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    try:
        from PyPDF2 import PdfReader
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("PyPDF2 is required for PDF extraction but is not installed") from exc

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
