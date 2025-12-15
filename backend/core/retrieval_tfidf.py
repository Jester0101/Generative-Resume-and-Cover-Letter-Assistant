from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .chunking import Chunk
from .preprocess import normalize_text


@dataclass(frozen=True)
class TfidfHit:
    chunk_id: str
    score: float
    method: str = "tfidf"


class TfidfIndex:
    def __init__(self, vectorizer: TfidfVectorizer, matrix, chunks: List[Chunk]):
        self.vectorizer = vectorizer
        self.matrix = matrix
        self.chunks = chunks

    @classmethod
    def build(cls, chunks: List[Chunk]) -> "TfidfIndex":
        docs = [normalize_text(c.text) for c in chunks]
        max_df = 1.0 if len(chunks) < 5 else 0.95
        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1, max_df=max_df)
        matrix = vectorizer.fit_transform(docs)
        return cls(vectorizer, matrix, chunks)


    def query(self, query_text: str, top_k: int = 5) -> List[TfidfHit]:
        qtxt = (query_text or "").strip()
        if not qtxt:
            return []
        q = self.vectorizer.transform([normalize_text(qtxt)])
        sims = cosine_similarity(q, self.matrix).ravel()
        if sims.size == 0:
            return []
        idxs = np.argsort(-sims)[:top_k]
        out: List[TfidfHit] = []
        for i in idxs:
            sc = float(sims[int(i)])
            if sc <= 0.0:
                continue
            out.append(TfidfHit(chunk_id=self.chunks[int(i)].chunk_id, score=sc))
        return out
