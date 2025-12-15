from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class ScoredChunk:
    chunk_id: str
    score_final: float
    score_tfidf: float
    score_bm25: float
    score_embed: float


@dataclass(frozen=True)
class RequirementMatch:
    requirement: str
    matched: bool
    score: float
    top_chunks: List[ScoredChunk]


@dataclass(frozen=True)
class MatchReport:
    match_score_must: int
    match_score_nice: int
    match_score_overall: int
    matched_requirements: List[str]
    missing_requirements: List[str]


def _minmax_map(hits: List[Tuple[str, float]]) -> Dict[str, float]:
    if not hits:
        return {}

    ids = [cid for cid, _ in hits]
    vals: List[float] = []
    for _, s in hits:
        try:
            vals.append(float(s))
        except Exception:
            vals.append(0.0)

    mx = max(vals)
    mn = min(vals)

    if mx == mn:
        if mx > 0.0:
            return {cid: 1.0 for cid in ids}
        return {cid: 0.0 for cid in ids}

    denom = mx - mn
    out: Dict[str, float] = {}
    for cid, v in zip(ids, vals):
        out[cid] = (v - mn) / denom
    return out


class HybridRanker:
    def __init__(
        self,
        w_bm25: float = 0.45,
        w_tfidf: float = 0.35,
        w_embed: float = 0.20,
        match_threshold: float = 0.62,
        top_k_chunks: int = 5,
        score_weight_must: float = 0.7,
    ):
        s = w_bm25 + w_tfidf + w_embed
        self.w_bm25 = w_bm25 / s
        self.w_tfidf = w_tfidf / s
        self.w_embed = w_embed / s
        self.match_threshold = match_threshold
        self.top_k_chunks = top_k_chunks
        self.score_weight_must = float(score_weight_must)

    def rank_requirement(
        self,
        requirement: str,
        hits_tfidf: List[Tuple[str, float]],
        hits_bm25: List[Tuple[str, float]],
        hits_embed: List[Tuple[str, float]],
    ) -> RequirementMatch:
        n_tfidf = _minmax_map(hits_tfidf)
        n_bm25 = _minmax_map(hits_bm25)
        n_embed = _minmax_map(hits_embed)

        all_ids = set(n_tfidf.keys()) | set(n_bm25.keys()) | set(n_embed.keys())
        scored: List[ScoredChunk] = []
        for cid in all_ids:
            s_t = float(n_tfidf.get(cid, 0.0))
            s_b = float(n_bm25.get(cid, 0.0))
            s_e = float(n_embed.get(cid, 0.0))
            final = self.w_tfidf * s_t + self.w_bm25 * s_b + self.w_embed * s_e
            scored.append(
                ScoredChunk(
                    chunk_id=cid,
                    score_final=float(final),
                    score_tfidf=s_t,
                    score_bm25=s_b,
                    score_embed=s_e,
                )
            )

        scored.sort(key=lambda x: x.score_final, reverse=True)
        top = scored[: self.top_k_chunks]
        best = float(top[0].score_final) if top else 0.0
        matched = best >= self.match_threshold
        return RequirementMatch(requirement=requirement, matched=matched, score=best, top_chunks=top)

    def build_report(
        self,
        matches: List[RequirementMatch],
        must_have: List[str],
        nice_to_have: List[str],
    ) -> MatchReport:
        if not matches:
            return MatchReport(
                match_score_must=0,
                match_score_nice=0,
                match_score_overall=0,
                matched_requirements=[],
                missing_requirements=[],
            )

        matched = [m.requirement for m in matches if m.matched]
        missing = [m.requirement for m in matches if not m.matched]

        must_set = set(must_have or [])
        nice_set = set(nice_to_have or [])

        must_total = len(must_set)
        nice_total = len(nice_set)

        must_matched = sum(1 for r in matched if r in must_set)
        nice_matched = sum(1 for r in matched if r in nice_set)

        score_must = int(round(100.0 * (must_matched / must_total))) if must_total > 0 else 0
        score_nice = int(round(100.0 * (nice_matched / nice_total))) if nice_total > 0 else 0

        w_must = float(self.score_weight_must)
        if w_must < 0.0:
            w_must = 0.0
        if w_must > 1.0:
            w_must = 1.0
        w_nice = 1.0 - w_must
        score_overall = int(round(w_must * score_must + w_nice * score_nice))

        return MatchReport(
            match_score_must=score_must,
            match_score_nice=score_nice,
            match_score_overall=score_overall,
            matched_requirements=matched,
            missing_requirements=missing,
        )
