from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

import numpy as np

from .chunking import Chunk
from .preprocess import normalize_text


@dataclass(frozen=True)
class EmbedHit:
    chunk_id: str
    score: float
    method: str = "embed"


class EmbedIndex:
    def __init__(self, chunks: List[Chunk], vectors: np.ndarray, index):
        self.chunks = chunks
        self.vectors = vectors
        self.index = index

    @staticmethod
    def l2_normalize(x: np.ndarray) -> np.ndarray:
        denom = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return x / denom

    @classmethod
    def build(
        cls,
        chunks: List[Chunk],
        embed_fn: Callable[[List[str]], np.ndarray],
        normalize: bool = True,
    ) -> "EmbedIndex":
        texts = [normalize_text(c.text) for c in chunks]
        vecs = embed_fn(texts).astype("float32")
        if normalize:
            vecs = cls.l2_normalize(vecs)

        import faiss

        d = int(vecs.shape[1])
        index = faiss.IndexFlatIP(d)
        index.add(vecs)
        return cls(chunks=chunks, vectors=vecs, index=index)

    def query(
        self,
        query_text: str,
        embed_fn: Callable[[List[str]], np.ndarray],
        top_k: int = 5,
        normalize: bool = True,
    ) -> List[EmbedHit]:
        qtxt = (query_text or "").strip()
        if not qtxt:
            return []
        q = embed_fn([normalize_text(qtxt)]).astype("float32")
        if normalize:
            q = self.l2_normalize(q)

        scores, idxs = self.index.search(q, top_k)
        out: List[EmbedHit] = []
        for sc, ix in zip(scores[0].tolist(), idxs[0].tolist()):
            if ix < 0:
                continue
            scf = float(sc)
            if scf <= 0.0:
                continue
            out.append(EmbedHit(chunk_id=self.chunks[int(ix)].chunk_id, score=scf))
        return out
