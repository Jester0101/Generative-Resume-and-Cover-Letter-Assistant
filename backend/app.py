from __future__ import annotations

import streamlit as st

from config import AppConfig
from orchestrator import run_pipeline
from core.pdf_extract import extract_text_from_pdf_bytes


st.set_page_config(page_title="CV-Agent", layout="wide")
st.title("CV-Agent")


with st.expander("Optional targeting (for company-specific cover letter)", expanded=True):
    company_name = st.text_input("Company name (optional)")
    role_title = st.text_input("Role title (optional)")

col1, col2 = st.columns(2)

with col1:
    jd_text = st.text_area("Job Description", height=360)

with col2:
    st.write("Profile / Resume (paste text OR upload PDF)")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded is not None:
        try:
            extracted = extract_text_from_pdf_bytes(uploaded.read())
            profile_text = st.text_area(
                "Extracted text (editable)",
                value=extracted,
                height=360,
            )
        except Exception as e:
            st.error(f"PDF extraction failed: {e}")
            profile_text = st.text_area("Profile / Resume", height=360)
    else:
        profile_text = st.text_area("Profile / Resume", height=360)

opt_col1, opt_col2, opt_col3, opt_col4, opt_col5 = st.columns(5)
with opt_col1:
    use_tfidf = st.checkbox("TF-IDF", value=True)
with opt_col2:
    use_bm25 = st.checkbox("BM25", value=True)
with opt_col3:
    use_embeddings = st.checkbox("Embeddings", value=False)
with opt_col4:
    use_llm_jd_classifier = st.checkbox("LLM JD Classify", value=False)
with opt_col5:
    use_llm_editor = st.checkbox("LLM Editor", value=True)

run_btn = st.button("Run", type="primary")

if run_btn:
    final_jd_text = jd_text or ""
    prefix_lines: list[str] = []

    if company_name and company_name.strip():
        prefix_lines.append(f"Company: {company_name.strip()}")
    if role_title and role_title.strip():
        prefix_lines.append(f"Role: {role_title.strip()}")

    if prefix_lines:
        final_jd_text = "\n".join(prefix_lines) + "\n\n" + final_jd_text

    cfg = AppConfig(
        use_tfidf=use_tfidf,
        use_bm25=use_bm25,
        use_embeddings=use_embeddings,
        use_llm_jd_classifier=use_llm_jd_classifier,
        use_llm_editor=use_llm_editor,
    )

    out = run_pipeline(final_jd_text, profile_text, cfg=cfg)

    tabs = st.tabs(["Match", "Evidence", "Resume Bullets", "Cover Letter", "Warnings", "JSON"])

    with tabs[0]:
        st.metric("Match Score (Overall)", out["match_report"]["match_score_overall"])
        st.metric("Must-have Score", out["match_report"]["match_score_must"])
        st.metric("Nice-to-have Score", out["match_report"]["match_score_nice"])

        st.subheader("Matched Requirements")
        st.write(out["match_report"]["matched_requirements"])
        st.subheader("Missing Requirements")
        st.write(out["match_report"]["missing_requirements"])

    with tabs[1]:
        st.subheader("Evidence Map")
        st.json(out["evidence_map"])

    with tabs[2]:
        st.subheader("Resume Bullets")
        bullets = out["generation"].get("resume_bullets", [])
        for b in bullets:
            st.write(f"- {b.get('text','')}")
            st.caption(f"evidence: {b.get('evidence_chunks', [])}")

    with tabs[3]:
        st.subheader("Cover Letter")
        st.write(out["generation"].get("cover_letter", {}).get("text", ""))

    with tabs[4]:
        st.subheader("Validation")
        st.write(out["validation"])
        st.subheader("Generation Warnings")
        st.write(out["generation"].get("warnings", []))

    with tabs[5]:
        st.json(out)
