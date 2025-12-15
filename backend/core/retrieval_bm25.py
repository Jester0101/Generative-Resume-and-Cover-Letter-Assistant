from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from rank_bm25 import BM25Okapi

from .chunking import Chunk
from .preprocess import tokenize


@dataclass(frozen=True)
class BM25Hit:
    chunk_id: str
    score: float
    method: str = "bm25"


class BM25Index:
    def __init__(self, bm25: BM25Okapi, chunks: List[Chunk]):
        self.bm25 = bm25
        self.chunks = chunks

    @classmethod
    def build(cls, chunks: List[Chunk]) -> "BM25Index":
        corpus = [c.tokens for c in chunks]
        bm25 = BM25Okapi(corpus)
        return cls(bm25, chunks)

    def query(self, query_text: str, top_k: int = 5) -> List[BM25Hit]:
        q_tokens = tokenize(query_text or "")
        if not q_tokens:
            return []
        scores = np.asarray(self.bm25.get_scores(q_tokens), dtype=float)
        idxs = np.argsort(-scores)[:top_k]
        out: List[BM25Hit] = []
        for i in idxs:
            sc = float(scores[int(i)])
            if sc <= 0.0:
                continue
            out.append(BM25Hit(chunk_id=self.chunks[int(i)].chunk_id, score=sc))
        return out
