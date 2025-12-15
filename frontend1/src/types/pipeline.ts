export type RunRequest = {
  job_description: string;
  profile_text: string;
  company_name?: string;
  role_title?: string;
  use_tfidf?: boolean;
  use_bm25?: boolean;
  use_embeddings?: boolean;
  use_llm_jd_classifier?: boolean;
  use_llm_editor?: boolean;
};

export type MatchReport = {
  match_score_overall: number;
  match_score_must: number;
  match_score_nice: number;
  matched_requirements: string[];
  missing_requirements: string[];
};

export type EvidenceChunk = {
  chunk_id: string;
  section: string;
  text: string;
  skills_found: string[];
  scores: {
    final: number;
    tfidf: number;
    bm25: number;
    embed: number;
  };
};

export type EvidenceItem = {
  requirement: string;
  matched: boolean;
  score: number;
  chunks: EvidenceChunk[];
};

export type Generation = {
  resume_bullets: {
    text: string;
    evidence_chunks: string[];
    skills_used?: string[];
  }[];
  cover_letter: {
    text: string;
    evidence_chunks: string[];
  };
  warnings?: string[];
};

export type ValidationWarning = {
  code: string;
  message: string;
  path: string;
};

export type PipelineResponse = {
  jd: {
    company_name?: string;
    role_title?: string;
    must_have_skills?: string[];
    nice_to_have_skills?: string[];
    responsibilities?: string[];
    keywords?: string[];
    [key: string]: unknown;
  };
  match_report: MatchReport;
  evidence_map: Record<string, EvidenceItem>;
  generation: Generation;
  validation: {
    ok: boolean;
    warnings: ValidationWarning[];
  };
};

