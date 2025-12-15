from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _chat_json(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    return json.loads(content)


def generate_with_llm(
    jd_struct: Dict[str, Any],
    match_report: Dict[str, Any],
    evidence_map: Dict[str, Any],
    user_profile_text: str,
    model: str,
    client: Optional[OpenAI] = None,
    fewshot_examples: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    c = client or OpenAI()

    
    prompt_path = os.path.join("prompts", "generate_resume.json.txt")
    system = _read_text(prompt_path)

    payload: Dict[str, Any] = {
        "jd": jd_struct,  
        "match_report": match_report,
        "evidence_map": evidence_map,
        "profile_text": user_profile_text,
    }

    if fewshot_examples:
        payload["fewshot_examples"] = fewshot_examples

    user = json.dumps(payload, ensure_ascii=False)

    out = _chat_json(c, model=model, system=system, user=user, temperature=0.2)

    # Defensive defaults
    out.setdefault("resume_bullets", [])
    out.setdefault("cover_letter", {"text": "", "evidence_chunks": []})
    out.setdefault("warnings", [])

    if not isinstance(out.get("resume_bullets"), list):
        out["resume_bullets"] = []
    if not isinstance(out.get("cover_letter"), dict):
        out["cover_letter"] = {"text": "", "evidence_chunks": []}
    if not isinstance(out.get("warnings"), list):
        out["warnings"] = []

    # Normalize bullet item shape
    cleaned_bullets: List[Dict[str, Any]] = []
    for b in out["resume_bullets"]:
        if not isinstance(b, dict):
            continue
        text = str(b.get("text", "")).strip()
        ev = b.get("evidence_chunks", [])
        skills = b.get("skills_used", [])
        if not isinstance(ev, list):
            ev = []
        if not isinstance(skills, list):
            skills = []
        cleaned_bullets.append(
            {
                "text": text,
                "evidence_chunks": [str(x) for x in ev],
                "skills_used": [str(x) for x in skills],
            }
        )

    cover = out["cover_letter"]
    ctext = str(cover.get("text", "")).strip()
    cev = cover.get("evidence_chunks", [])
    if not isinstance(cev, list):
        cev = []

    out["resume_bullets"] = cleaned_bullets
    out["cover_letter"] = {"text": ctext, "evidence_chunks": [str(x) for x in cev]}
    out["warnings"] = [str(x) for x in out["warnings"]]

    return out
