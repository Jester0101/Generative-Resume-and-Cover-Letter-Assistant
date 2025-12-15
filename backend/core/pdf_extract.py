
from __future__ import annotations

import re

def _fix_pdf_text_layout(text: str) -> str:
    """
    Делает текст более "CV-friendly":
    - гарантирует переносы после ключевых секций
    - нормализует пробелы
    """
    t = (text or "").replace("\r", "\n")

    
    секции = [
        "Profile:", "Technical Skills:", "Projects:", "Education:", "Languages:",
        "Profile", "Technical Skills", "Projects", "Education", "Languages",
        "SUMMARY", "TECHNICAL SKILLS", "PROJECTS", "EDUCATION", "LANGUAGES",
    ]
    for s in секции:
        
        t = re.sub(rf"(?<!\n)\s+({re.escape(s)})", r"\n\1", t)

    
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    return t.strip()


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        import pdfplumber
    except Exception as e:
        raise RuntimeError("pdfplumber is required. Install it: pip install pdfplumber") from e

    parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")

    return _fix_pdf_text_layout("\n\n".join(parts))


import io
