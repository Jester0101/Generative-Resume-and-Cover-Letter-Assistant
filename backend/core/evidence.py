from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .chunking import Chunk
from .ranker import RequirementMatch, ScoredChunk
from .skill_taxonomy import SkillTaxonomy


@dataclass(frozen=True)
class EvidenceItem:
    requirement: str
    matched: bool
    score: float
    chunks: List[Dict]


class EvidenceMapBuilder:
    def __init__(self, taxonomy: SkillTaxonomy):
        self.taxonomy = taxonomy

    def build(
        self,
        matches: List[RequirementMatch],
        chunks: List[Chunk],
    ) -> Dict[str, EvidenceItem]:
        chunk_map: Dict[str, Chunk] = {c.chunk_id: c for c in chunks}
        out: Dict[str, EvidenceItem] = {}

        for m in matches:
            packed: List[Dict] = []
            for sc in m.top_chunks:
                ch = chunk_map.get(sc.chunk_id)
                if not ch:
                    continue
                found_skills = sorted(self.taxonomy.extract_skills(ch.text))
                packed.append(
                    {
                        "chunk_id": ch.chunk_id,
                        "section": ch.section,
                        "text": ch.text,
                        "skills_found": found_skills,
                        "scores": {
                            "final": sc.score_final,
                            "tfidf": sc.score_tfidf,
                            "bm25": sc.score_bm25,
                            "embed": sc.score_embed,
                        },
                    }
                )

            out[m.requirement] = EvidenceItem(
                requirement=m.requirement,
                matched=m.matched,
                score=m.score,
                chunks=packed,
            )

        return out
