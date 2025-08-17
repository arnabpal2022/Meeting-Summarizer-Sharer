from io import BytesIO
from typing import Optional
from pypdf import PdfReader

def extract_text_from_pdf(data: bytes) -> str:
    """
    Extracts text from a PDF byte stream. Returns a single concatenated string.
    Note: image-only PDFs will produce little or no text; OCR is not included here.
    """
    if not data:
        return ""
    bio = BytesIO(data)
    reader = PdfReader(bio)
    parts: list[str] = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        if t:
            parts.append(t.strip())
    text = "\n\n".join([p for p in parts if p])
    return text.strip()
