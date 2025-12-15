from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Set

from .skill_taxonomy import SkillTaxonomy
from .preprocess import normalize_text


@dataclass(frozen=True)
class ValidationWarning:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    warnings: List[ValidationWarning]


def _collect_evidence_chunk_ids(evidence_map: Dict[str, Any]) -> Set[str]:
    ids: Set[str] = set()
    for _, item in evidence_map.items():
        chunks = item.get("chunks") if isinstance(item, dict) else getattr(item, "chunks", [])
        for ch in chunks:
            cid = ch.get("chunk_id")
            if cid:
                ids.add(str(cid))
    return ids


def validate_generation(
    generation: Dict[str, Any],
    evidence_map: Dict[str, Any],
    taxonomy: SkillTaxonomy,
    max_bullet_words: int = 28,
) -> ValidationResult:
    warnings: List[ValidationWarning] = []
    evidence_ids = _collect_evidence_chunk_ids(evidence_map)

    bullets = generation.get("resume_bullets", [])
    if not isinstance(bullets, list):
        warnings.append(ValidationWarning("FORMAT", "resume_bullets must be a list", "resume_bullets"))
        return ValidationResult(ok=False, warnings=warnings)

    for i, b in enumerate(bullets):
        path = f"resume_bullets[{i}]"
        if not isinstance(b, dict):
            warnings.append(ValidationWarning("FORMAT", "bullet must be an object", path))
            continue
        text = str(b.get("text", "")).strip()
        ev = b.get("evidence_chunks", [])
        skills_used = b.get("skills_used", [])

        if not text:
            warnings.append(ValidationWarning("EMPTY", "bullet text is empty", f"{path}.text"))
        else:
            wc = len(text.split())
            if wc > max_bullet_words:
                warnings.append(ValidationWarning("LENGTH", f"bullet too long: {wc} words", f"{path}.text"))
            if " i " in f" {normalize_text(text)} " or " my " in f" {normalize_text(text)} ":
                warnings.append(ValidationWarning("STYLE", "first-person pronoun in resume bullet", f"{path}.text"))

        if not isinstance(ev, list) or not ev:
            warnings.append(ValidationWarning("GROUNDING", "missing evidence_chunks", f"{path}.evidence_chunks"))
        else:
            for j, cid in enumerate(ev):
                if str(cid) not in evidence_ids:
                    warnings.append(ValidationWarning("GROUNDING", "unknown chunk_id in evidence_chunks", f"{path}.evidence_chunks[{j}]"))

        if isinstance(skills_used, list):
            for j, s in enumerate(skills_used):
                if not taxonomy.is_known_skill(str(s)):
                    warnings.append(ValidationWarning("SKILL", "unknown skill in skills_used", f"{path}.skills_used[{j}]"))
        else:
            warnings.append(ValidationWarning("FORMAT", "skills_used must be a list", f"{path}.skills_used"))

    cover = generation.get("cover_letter", {})
    if isinstance(cover, dict):
        ev = cover.get("evidence_chunks", [])
        if not isinstance(ev, list) or not ev:
            warnings.append(ValidationWarning("GROUNDING", "missing evidence_chunks for cover_letter", "cover_letter.evidence_chunks"))
        else:
            for j, cid in enumerate(ev):
                if str(cid) not in evidence_ids:
                    warnings.append(ValidationWarning("GROUNDING", "unknown chunk_id in cover_letter evidence", f"cover_letter.evidence_chunks[{j}]"))
    else:
        warnings.append(ValidationWarning("FORMAT", "cover_letter must be an object", "cover_letter"))

    ok = all(w.code not in {"FORMAT"} for w in warnings)
    return ValidationResult(ok=ok, warnings=warnings)


def enforce_grounding(
    generation: Dict[str, Any],
    evidence_map: Dict[str, Any],
    taxonomy: SkillTaxonomy,
) -> Dict[str, Any]:
    evidence_ids = _collect_evidence_chunk_ids(evidence_map)

    bullets = generation.get("resume_bullets", [])
    if isinstance(bullets, list):
        cleaned: List[Dict[str, Any]] = []
        for b in bullets:
            if not isinstance(b, dict):
                continue
            text = str(b.get("text", "")).strip()
            ev = b.get("evidence_chunks", [])
            if not text or not isinstance(ev, list) or not ev:
                continue
            if any(str(cid) not in evidence_ids for cid in ev):
                continue
            skills_used = b.get("skills_used", [])
            if isinstance(skills_used, list):
                skills_used = [s for s in skills_used if taxonomy.is_known_skill(str(s))]
            cleaned.append({"text": text, "evidence_chunks": ev, "skills_used": skills_used})
        generation["resume_bullets"] = cleaned

    cover = generation.get("cover_letter", {})
    if isinstance(cover, dict):
        ev = cover.get("evidence_chunks", [])
        if not isinstance(ev, list) or not ev or any(str(cid) not in evidence_ids for cid in ev):
            generation["cover_letter"] = {"text": "", "evidence_chunks": []}

    return generation
