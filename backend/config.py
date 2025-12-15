from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    skills_yaml_path: str = "data/skills.yaml"
    stopwords_path: str = "data/stopwords.txt"
    fewshot_path: str = "data/fewshot_examples.json"

    outputs_dir: str = "outputs"
    exports_dir: str = "outputs/exports"
    last_run_path: str = "outputs/last_run.json"
    package_zip_path: str = "outputs/exports/package.zip"

    use_tfidf: bool = True
    use_bm25: bool = True
    use_embeddings: bool = False
    use_llm_jd_classifier: bool = False
    use_llm_editor: bool = False

    chunk_chars: int = 430
    overlap_chars: int = 60
    top_k_retrieval: int = 8

    w_bm25: float = 0.45
    w_tfidf: float = 0.35
    w_embed: float = 0.20
    match_threshold: float = 0.45
    top_k_chunks: int = 5

    max_bullet_words: int = 28

    require_lexical_support: bool = True
    score_weight_must: float = 0.7
