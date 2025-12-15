from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from config import AppConfig
from orchestrator import run_pipeline
from fastapi.middleware.cors import CORSMiddleware

class RunRequest(BaseModel):
    job_description: str
    profile_text: str
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    use_tfidf: Optional[bool] = True
    use_bm25: Optional[bool] = True
    use_embeddings: Optional[bool] = False
    use_llm_jd_classifier: Optional[bool] = False
    use_llm_editor: Optional[bool] = True



app = FastAPI()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True}




@app.post("/run")
def run(req: RunRequest) -> Dict[str, Any]:
    cfg = AppConfig(
        use_tfidf=bool(req.use_tfidf),
        use_bm25=bool(req.use_bm25),
        use_embeddings=bool(req.use_embeddings),
        use_llm_jd_classifier=bool(req.use_llm_jd_classifier),
        use_llm_editor=bool(req.use_llm_editor),
    )
    return run_pipeline(req.job_description, req.profile_text, cfg=cfg)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_methods=["*"],
    allow_headers=["*"],
)