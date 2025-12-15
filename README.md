

---

# Cover Letter Assistant — Backend

This project provides a **FastAPI backend** that analyzes a job description and a candidate profile to generate **grounded resume bullets and a tailored cover letter**.

The system matches job requirements against real evidence from the candidate’s profile and produces structured, verifiable outputs.

---

## What this backend does

Given a job description and a resume/profile, the backend:

* extracts required and optional job skills
* analyzes the candidate profile and splits it into evidence chunks
* matches job requirements to real profile evidence
* computes match scores (must-have, nice-to-have, overall)
* generates resume bullets and a cover letter grounded in that evidence
* validates and filters outputs to avoid hallucinations

---

## Requirements

* Python 3.10+
* pip
* OpenAI API key

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Environment variables

Create a `.env` file inside the `backend/` directory:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## Run the backend (API)

From the `backend/` directory:

```bash
uvicorn api:app --reload
```

API will be available at:

```
http://localhost:8000
```

Health check:

```
http://localhost:8000/health
```

API docs:

```
http://localhost:8000/docs
```

---

## Quick local testing via Streamlit

For quick manual testing with a simple UI, you can run the Streamlit app:

```bash
streamlit run app.py
```

This launches a lightweight interface for interacting with the backend logic without setting up any separate frontend.

---

## Main endpoint

### `POST /run`

Runs the complete analysis and generation pipeline.

Example request body:

```json
{
  "job_description": "Company: ExampleCorp\nRole: Backend Engineer\n\nWe are looking for Python and FastAPI experience.",
  "profile_text": "Built FastAPI services and worked extensively with Python.",
  "use_tfidf": true,
  "use_bm25": true,
  "use_embeddings": false,
  "use_llm_jd_classifier": false,
  "use_llm_editor": true
}
```

---

## Notes

* All generated content is grounded in the provided profile text.
* The backend can be tested either via FastAPI (`/docs`) or Streamlit.
* The system is frontend-agnostic and can be integrated with any client.

---


