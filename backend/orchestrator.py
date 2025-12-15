from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from config import AppConfig
from core.chunking import chunk_profile
from core.skill_taxonomy import SkillTaxonomy
from core.retrieval_tfidf import TfidfIndex
from core.retrieval_bm25 import BM25Index
from core.retrieval_embed import EmbedIndex
from core.ranker import HybridRanker, RequirementMatch
from core.evidence import EvidenceMapBuilder
from core.validators import validate_generation, enforce_grounding
from core.export import export_json, export_markdown, export_zip
from core.normalize import normalize_generation_payload

from agents.jd_parser_rules import parse_jd_rules
from agents.jd_classifier_llm import classify_jd_with_llm
from agents.generator_llm import generate_with_llm
from agents.editor_llm import edit_with_llm


def _read_lines(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(ln.strip() for ln in f.readlines() if ln.strip())


def _read_json(path: str) -> Any:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_dirs(cfg: AppConfig) -> None:
    os.makedirs(cfg.outputs_dir, exist_ok=True)
    os.makedirs(cfg.exports_dir, exist_ok=True)


def _requirement_list(jd_struct: Dict[str, Any]) -> List[str]:
    reqs: List[str] = []
    for s in jd_struct.get("must_have_skills", []) or []:
        reqs.append(str(s))
    for s in jd_struct.get("nice_to_have_skills", []) or []:
        reqs.append(str(s))
    return [r for r in reqs if r.strip()]


def _openai_client() -> OpenAI:
    load_dotenv()
    return OpenAI()


def _embed_fn_factory(client: OpenAI, model: str):
    def embed_fn(texts: List[str]):
        resp = client.embeddings.create(model=model, input=texts)
        vecs = [d.embedding for d in resp.data]
        import numpy as np
        return np.array(vecs, dtype="float32")
    return embed_fn


def _extract_company_role(jd_text: str) -> Tuple[str, str]:
    """
    Looks for:
      Company: <name>
      Role: <title>
    anywhere in jd_text (prefer first match).
    """
    company = ""
    role = ""

    
    m_company = re.search(r"(?im)^\s*company\s*:\s*(.+?)\s*$", jd_text or "")
    m_role = re.search(r"(?im)^\s*role\s*:\s*(.+?)\s*$", jd_text or "")

    if m_company:
        company = m_company.group(1).strip()
    if m_role:
        role = m_role.group(1).strip()

    return company, role


def _adaptive_weights(cfg: AppConfig) -> tuple[float, float, float]:
    
    enabled = {
        "bm25": bool(cfg.use_bm25),
        "tfidf": bool(cfg.use_tfidf),
        "embed": bool(cfg.use_embeddings),
    }

    
    wb, wt, we = float(cfg.w_bm25), float(cfg.w_tfidf), float(cfg.w_embed)

    
    wb = wb if enabled["bm25"] else 0.0
    wt = wt if enabled["tfidf"] else 0.0
    we = we if enabled["embed"] else 0.0

    s = wb + wt + we

    
    if s <= 0.0:
        return (0.0, 1.0, 0.0)

    return (wb / s, wt / s, we / s)


def _adaptive_threshold(cfg: AppConfig, w_bm25: float, w_tfidf: float, w_embed: float) -> float:
    
    enabled_count = sum([bool(cfg.use_bm25), bool(cfg.use_tfidf), bool(cfg.use_embeddings)])

    
    if enabled_count == 1:
        
        return min(float(cfg.match_threshold), 0.30)

    return float(cfg.match_threshold)


def run_pipeline(
    jd_text: str,
    profile_text: str,
    cfg: Optional[AppConfig] = None,
) -> Dict[str, Any]:
    cfg = cfg or AppConfig()
    _ensure_dirs(cfg)

    taxonomy = SkillTaxonomy.from_yaml(cfg.skills_yaml_path)
    stopwords = _read_lines(cfg.stopwords_path)
    fewshot = _read_json(cfg.fewshot_path) or []

    client = _openai_client()

    model_classify = os.getenv("OPENAI_MODEL_CLASSIFY", "gpt-4o-mini")
    model_generate = os.getenv("OPENAI_MODEL_GENERATE", "gpt-4o-mini")
    model_edit = os.getenv("OPENAI_MODEL_EDIT", "gpt-4o-mini")
    embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

    
    extracted_company, extracted_role = _extract_company_role(jd_text or "")

    
    extracted = parse_jd_rules(jd_text or "", taxonomy)

    
    if cfg.use_llm_jd_classifier:
        jd_struct = classify_jd_with_llm(jd_text or "", extracted, model=model_classify, client=client)
    else:
        jd_struct = {
            "must_have_skills": extracted.get("must_have_skills", []),
            "nice_to_have_skills": extracted.get("nice_to_have_skills", []),
            "responsibilities": extracted.get("responsibilities", []),
            "keywords": extracted.get("keywords", []),
        }

    
    jd_struct.setdefault("company_name", "")
    jd_struct.setdefault("role_title", "")

    if extracted_company:
        jd_struct["company_name"] = extracted_company
    if extracted_role:
        jd_struct["role_title"] = extracted_role

    
    chunks = chunk_profile(
        profile_text or "",
        stopwords=stopwords,
        chunk_chars=cfg.chunk_chars,
        overlap_chars=cfg.overlap_chars,
    )

    
    tfidf_index = TfidfIndex.build(chunks) if cfg.use_tfidf else None
    bm25_index = BM25Index.build(chunks) if cfg.use_bm25 else None

    embed_index = None
    embed_fn = None
    if cfg.use_embeddings:
        embed_fn = _embed_fn_factory(client, embed_model)
        embed_index = EmbedIndex.build(chunks, embed_fn=embed_fn, normalize=True)

    
    w_bm25, w_tfidf, w_embed = _adaptive_weights(cfg)
    match_threshold = _adaptive_threshold(cfg, w_bm25, w_tfidf, w_embed)

    ranker = HybridRanker(
        w_bm25=w_bm25,
        w_tfidf=w_tfidf,
        w_embed=w_embed,
        match_threshold=match_threshold,
        top_k_chunks=cfg.top_k_chunks,
        score_weight_must=getattr(cfg, "score_weight_must", 0.7),
    )


    requirements = _requirement_list(jd_struct)
    matches: List[RequirementMatch] = []

    for req in requirements:
        hits_tfidf: List[Tuple[str, float]] = []
        hits_bm25: List[Tuple[str, float]] = []
        hits_embed: List[Tuple[str, float]] = []

        if tfidf_index:
            for h in tfidf_index.query(req, top_k=cfg.top_k_retrieval):
                hits_tfidf.append((h.chunk_id, float(h.score)))

        if bm25_index:
            for h in bm25_index.query(req, top_k=cfg.top_k_retrieval):
                hits_bm25.append((h.chunk_id, float(h.score)))

        if embed_index and embed_fn:
            for h in embed_index.query(req, embed_fn=embed_fn, top_k=cfg.top_k_retrieval):
                hits_embed.append((h.chunk_id, float(h.score)))

        matches.append(ranker.rank_requirement(req, hits_tfidf, hits_bm25, hits_embed))

    report = ranker.build_report(
        matches,
        must_have=jd_struct.get("must_have_skills", []) or [],
        nice_to_have=jd_struct.get("nice_to_have_skills", []) or [],
    )

    match_report = {
        "match_score_must": report.match_score_must,
        "match_score_nice": report.match_score_nice,
        "match_score_overall": report.match_score_overall,
        "matched_requirements": report.matched_requirements,
        "missing_requirements": report.missing_requirements,
    }

    
    evidence_builder = EvidenceMapBuilder(taxonomy)
    evidence_map_items = evidence_builder.build(matches, chunks)

    evidence_map: Dict[str, Any] = {}
    for k, v in evidence_map_items.items():
        evidence_map[k] = {
            "requirement": v.requirement,
            "matched": v.matched,
            "score": v.score,
            "chunks": v.chunks,
        }

   
    generation_raw = generate_with_llm(
        jd_struct=jd_struct,
        match_report=match_report,
        evidence_map=evidence_map,
        user_profile_text=profile_text or "",
        model=model_generate,
        client=client,
        fewshot_examples=fewshot if isinstance(fewshot, list) else None,
    )

    generation = normalize_generation_payload(generation_raw)

    validation = validate_generation(
        generation=generation,
        evidence_map=evidence_map,
        taxonomy=taxonomy,
        max_bullet_words=cfg.max_bullet_words,
    )

    generation = enforce_grounding(generation, evidence_map, taxonomy)

    
    if cfg.use_llm_editor:
        warn_list = [{"code": w.code, "message": w.message, "path": w.path} for w in validation.warnings]

        edited_raw = edit_with_llm(
            generation=generation,
            validation_warnings=warn_list,
            evidence_map=evidence_map,
            model=model_edit,
            client=client,
        )

        generation = normalize_generation_payload(edited_raw)

        validation = validate_generation(
            generation=generation,
            evidence_map=evidence_map,
            taxonomy=taxonomy,
            max_bullet_words=cfg.max_bullet_words,
        )
        generation = enforce_grounding(generation, evidence_map, taxonomy)

    final_output = {
        "jd": jd_struct,
        "match_report": match_report,
        "evidence_map": evidence_map,
        "generation": generation,
        "validation": {
            "ok": bool(validation.ok),
            "warnings": [{"code": w.code, "message": w.message, "path": w.path} for w in validation.warnings],
        },
    }

    export_json(final_output, cfg.last_run_path)
    export_markdown({"generation": generation}, cfg.exports_dir)
    export_zip(cfg.exports_dir, cfg.package_zip_path)

    return final_output
