
from __future__ import annotations

from typing import Any, Dict


def normalize_generation_payload(payload: Any) -> Dict[str, Any]:

    if not isinstance(payload, dict):
        return {"resume_bullets": [], "cover_letter": {"text": "", "evidence_chunks": []}, "warnings": []}

   
    for key in ("format", "generation", "output", "result"):
        inner = payload.get(key)
        if isinstance(inner, dict) and ("resume_bullets" in inner or "cover_letter" in inner):
            payload = inner
            break

    
    resume_bullets = payload.get("resume_bullets")
    cover_letter = payload.get("cover_letter")
    warnings = payload.get("warnings")

    if not isinstance(resume_bullets, list):
        resume_bullets = []

    if not isinstance(cover_letter, dict):
        cover_letter = {"text": "", "evidence_chunks": []}
    else:
        if "text" not in cover_letter or not isinstance(cover_letter.get("text"), str):
            cover_letter["text"] = ""
        if "evidence_chunks" not in cover_letter or not isinstance(cover_letter.get("evidence_chunks"), list):
            cover_letter["evidence_chunks"] = []

    if not isinstance(warnings, list):
        warnings = []

    return {
        "resume_bullets": resume_bullets,
        "cover_letter": cover_letter,
        "warnings": warnings,
    }
