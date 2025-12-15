from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple

from core.preprocess import normalize_text, tokenize
from core.skill_taxonomy import SkillTaxonomy


def _split_sentences(text: str) -> List[str]:
    t = (text or "").replace("\r\n", "\n")
    parts = re.split(r"(?<=[\.\!\?\:])\s+|\n+", t)
    out = [p.strip() for p in parts if p and p.strip()]
    return out


def _extract_keywords(text: str, top_k: int = 25) -> List[str]:
    toks = tokenize(text or "")
    freq: Dict[str, int] = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    items = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [k for k, _ in items[:top_k]]


def _is_must_sentence(s: str) -> bool:
    t = normalize_text(s)
    must_markers = [
        "must", "required", "requirements", "you will need", "need to", "mandatory",
        "essential", "minimum", "strong experience", "proven experience",
    ]
    return any(m in t for m in must_markers)


def _is_nice_sentence(s: str) -> bool:
    t = normalize_text(s)
    nice_markers = [
        "nice to have", "nice-to-have", "preferred", "a plus", "plus", "advantage",
        "bonus", "good to have", "would be great",
    ]
    return any(m in t for m in nice_markers)


def _extract_responsibilities(text: str) -> List[str]:
    lines = [ln.strip() for ln in (text or "").splitlines()]
    out: List[str] = []
    for ln in lines:
        if not ln:
            continue
        if re.match(r"^(\-|\*|•)\s+", ln):
            item = re.sub(r"^(\-|\*|•)\s+", "", ln).strip()
            if item:
                out.append(item)
    if out:
        return out[:30]
    sentences = _split_sentences(text)
    candidates = [s for s in sentences if len(s.split()) >= 6]
    return candidates[:12]


def parse_jd_rules(jd_text: str, taxonomy: SkillTaxonomy) -> Dict[str, Any]:
    txt = jd_text or ""
    sentences = _split_sentences(txt)

    must_skills: Set[str] = set()
    nice_skills: Set[str] = set()
    other_skills: Set[str] = set()

    for s in sentences:
        found = taxonomy.extract_skills(s)
        if not found:
            continue
        if _is_nice_sentence(s):
            nice_skills |= found
        elif _is_must_sentence(s):
            must_skills |= found
        else:
            other_skills |= found

    nice_skills -= must_skills
    other_skills -= must_skills
    other_skills -= nice_skills

    if not must_skills and other_skills:
        must_skills |= set(list(other_skills)[: min(6, len(other_skills))])
        other_skills -= must_skills

    keywords = _extract_keywords(txt, top_k=30)
    responsibilities = _extract_responsibilities(txt)

    return {
        "must_have_skills": sorted(must_skills),
        "nice_to_have_skills": sorted(nice_skills),
        "other_skills": sorted(other_skills),
        "responsibilities": responsibilities,
        "keywords": keywords,
    }
