from __future__ import annotations

import re
from typing import Iterable, List, Set

DEFAULT_STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "to", "of", "in", "for", "with", "on", "at", "by",
    "is", "are", "was", "were", "be", "been", "as", "that", "this", "it",
    "i", "you", "he", "she", "they", "we", "my", "our", "your", "their",
}


def normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.lower().replace("\u00a0", " ")
    t = re.sub(r"[^\w\s\+\#\.\-/]", " ", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def tokenize(text: str, stopwords: Set[str] | None = None, min_len: int = 2) -> List[str]:
    stop = stopwords if stopwords is not None else DEFAULT_STOPWORDS
    t = normalize_text(text)
    tokens = re.split(r"[\s/,\.;:\(\)\[\]\{\}]+", t)
    out: List[str] = []
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        if len(tok) < min_len:
            continue
        if tok in stop:
            continue
        out.append(tok)
    return out


def join_tokens(tokens: Iterable[str]) -> str:
    return " ".join(list(tokens))
