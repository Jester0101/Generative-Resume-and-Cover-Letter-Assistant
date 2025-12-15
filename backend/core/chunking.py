from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .preprocess import normalize_text, tokenize


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    section: str
    text: str
    tokens: List[str]


def _split_sections(profile_text: str) -> Dict[str, str]:
    text = (profile_text or "").strip()
    if not text:
        return {"profile": ""}

    lines = [ln.rstrip() for ln in text.splitlines()]
    sections: Dict[str, List[str]] = {"profile": []}
    current = "profile"

    markers = {
        "summary": {"summary", "profile", "about"},
        "experience": {"experience", "work experience", "employment"},
        "projects": {"projects", "project"},
        "skills": {"skills", "technical skills"},
        "education": {"education"},
    }

    def detect_section(line: str) -> str | None:
        key = normalize_text(line).strip(":").strip()
        for sec, names in markers.items():
            if key in names:
                return sec
        return None

    for ln in lines:
        sec = detect_section(ln)
        if sec:
            current = sec
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(ln)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _paragraphs(text: str) -> List[str]:
    raw = text.split("\n")
    paras: List[str] = []
    buf: List[str] = []
    for ln in raw:
        if ln.strip() == "":
            if buf:
                paras.append("\n".join(buf).strip())
                buf = []
        else:
            buf.append(ln)
    if buf:
        paras.append("\n".join(buf).strip())
    return [p for p in paras if p]


def chunk_profile(
    profile_text: str,
    stopwords: set[str] | None = None,
    chunk_chars: int = 1200,
    overlap_chars: int = 200,
) -> List[Chunk]:
    sections = _split_sections(profile_text)
    chunks: List[Chunk] = []
    idx = 0

    for section, body in sections.items():
        if not body:
            continue

        paras = _paragraphs(body) or [body]
        merged = "\n\n".join(paras)

        start = 0
        while start < len(merged):
            end = min(len(merged), start + chunk_chars)
            slice_text = merged[start:end].strip()
            if slice_text:
                chunk_id = f"{section}_{idx:03d}"
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        section=section,
                        text=slice_text,
                        tokens=tokenize(slice_text, stopwords=stopwords),
                    )
                )
                idx += 1
            if end == len(merged):
                break
            start = max(0, end - overlap_chars)

    if not chunks:
        txt = (profile_text or "").strip()
        chunks.append(
            Chunk(
                chunk_id="profile_000",
                section="profile",
                text=txt,
                tokens=tokenize(txt, stopwords=stopwords),
            )
        )

    return chunks
