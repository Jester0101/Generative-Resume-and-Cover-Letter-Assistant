from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

EXPECTED_KEYS = {"resume_bullets", "cover_letter", "warnings"}


def _read_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _is_valid_generation_shape(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if set(obj.keys()) != EXPECTED_KEYS:
        return False

    if not isinstance(obj.get("resume_bullets"), list):
        return False
    if not isinstance(obj.get("warnings"), list):
        return False

    cl = obj.get("cover_letter")
    if not isinstance(cl, dict):
        return False
    if "text" not in cl or "evidence_chunks" not in cl:
        return False
    if not isinstance(cl["evidence_chunks"], list):
        return False

    for b in obj["resume_bullets"]:
        if not isinstance(b, dict):
            return False
        if "text" not in b or "evidence_chunks" not in b or "skills_used" not in b:
            return False
        if not isinstance(b["evidence_chunks"], list):
            return False
        if not isinstance(b["skills_used"], list):
            return False

    return True


def _fallback(generation: Dict[str, Any], msg: str) -> Dict[str, Any]:
    out = dict(generation)
    out.setdefault("resume_bullets", [])
    out.setdefault("cover_letter", {"text": "", "evidence_chunks": []})
    out.setdefault("warnings", [])
    if not isinstance(out["warnings"], list):
        out["warnings"] = []
    out["warnings"].append(msg)
    return out


def edit_with_llm(
    generation: Dict[str, Any],
    validation_warnings: List[Dict[str, Any]],
    evidence_map: Dict[str, Any],
    model: str,
    client: Optional[OpenAI] = None,
) -> Dict[str, Any]:
    c = client or OpenAI()

    
    prompt_path = os.path.join("prompts", "edit_style.json.txt")
    system = _read_prompt(prompt_path)

    payload = {
        "generation": generation,
        "validation_warnings": validation_warnings,
        "evidence_map": evidence_map,
    }

    try:
        resp = c.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        edited = json.loads(raw)
    except Exception:
        return _fallback(generation, "LLM editor failed or returned invalid JSON; kept original generation.")

    if not _is_valid_generation_shape(edited):
        return _fallback(generation, "LLM editor returned unexpected schema; kept original generation.")

    
    for b in edited["resume_bullets"]:
        if not isinstance(b.get("evidence_chunks"), list) or not isinstance(b.get("skills_used"), list):
            return _fallback(generation, "LLM editor corrupted bullet schema; kept original generation.")
    if not isinstance(edited["cover_letter"].get("evidence_chunks"), list):
        return _fallback(generation, "LLM editor corrupted cover_letter schema; kept original generation.")

    return edited
