from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openai import OpenAI


def _chat_json(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.1,
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


def classify_jd_with_llm(
    jd_text: str,
    extracted: Dict[str, Any],
    model: str,
    client: Optional[OpenAI] = None,
) -> Dict[str, Any]:
    c = client or OpenAI()

    skills = {
        "must_have_skills": extracted.get("must_have_skills", []),
        "nice_to_have_skills": extracted.get("nice_to_have_skills", []),
        "other_skills": extracted.get("other_skills", []),
        "keywords": extracted.get("keywords", []),
    }

    system = (
        "You convert a job description into a strict JSON structure for downstream retrieval and matching. "
        "You must not invent skills not present in the provided candidate skill lists unless they are explicitly stated in the job description. "
        "Return only valid JSON."
    )

    user = json.dumps(
        {
            "job_description": jd_text or "",
            "candidate_skill_lists": skills,
            "required_output_schema": {
                "must_have_skills": "array of strings",
                "nice_to_have_skills": "array of strings",
                "responsibilities": "array of strings",
                "keywords": "array of strings",
            },
            "instructions": [
                "Use must_have_skills and nice_to_have_skills primarily from candidate_skill_lists, adjusting only if the job description clearly indicates otherwise.",
                "Responsibilities should be concise bullet-like statements.",
                "Keywords should be short tokens or short phrases.",
            ],
        },
        ensure_ascii=False,
    )

    out = _chat_json(c, model=model, system=system, user=user, temperature=0.1)

    out.setdefault("must_have_skills", extracted.get("must_have_skills", []))
    out.setdefault("nice_to_have_skills", extracted.get("nice_to_have_skills", []))
    out.setdefault("responsibilities", extracted.get("responsibilities", []))
    out.setdefault("keywords", extracted.get("keywords", []))

    if not isinstance(out.get("must_have_skills"), list):
        out["must_have_skills"] = extracted.get("must_have_skills", [])
    if not isinstance(out.get("nice_to_have_skills"), list):
        out["nice_to_have_skills"] = extracted.get("nice_to_have_skills", [])
    if not isinstance(out.get("responsibilities"), list):
        out["responsibilities"] = extracted.get("responsibilities", [])
    if not isinstance(out.get("keywords"), list):
        out["keywords"] = extracted.get("keywords", [])

    out["must_have_skills"] = [str(x) for x in out["must_have_skills"]]
    out["nice_to_have_skills"] = [str(x) for x in out["nice_to_have_skills"]]
    out["responsibilities"] = [str(x) for x in out["responsibilities"]]
    out["keywords"] = [str(x) for x in out["keywords"]]

    return out
