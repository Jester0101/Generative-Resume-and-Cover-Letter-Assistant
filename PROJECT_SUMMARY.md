# Generative Resume and Cover Letter Assistant
## Project Summary & Technical Documentation

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Core Functionalities](#core-functionalities)
6. [Technical Stack](#technical-stack)
7. [Workflow & Pipeline](#workflow--pipeline)
8. [Key Features](#key-features)

---

## 🎯 Project Overview

**Generative Resume and Cover Letter Assistant** is an intelligent AI-powered system that analyzes job descriptions and candidate profiles to generate **grounded, evidence-based resume bullets and tailored cover letters**. The system ensures all generated content is verifiable by linking it to specific evidence chunks from the candidate's profile, preventing hallucinations and maintaining authenticity.

### Core Value Proposition
- **Grounded Generation**: All outputs are backed by evidence from the candidate's profile
- **Multi-Method Retrieval**: Combines TF-IDF, BM25, and semantic embeddings for robust matching
- **Transparent Evidence**: Provides detailed evidence maps showing how requirements match profile chunks
- **Configurable Pipeline**: Flexible retrieval and generation options for different use cases
- **Modern UI**: Clean, responsive interface with real-time feedback

---

## 🏗️ System Architecture

The system follows a **client-server architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  - React 19 + TypeScript                                     │
│  - shadcn/ui components                                      │
│  - PDF upload & text extraction                              │
│  - Real-time result visualization                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Backend (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Orchestrator (Main Pipeline)                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Retrieval│  │ Matching │  │ Evidence │  │Generation │ │
│  │  Engine  │  │  Engine  │  │  Builder │  │  Engine   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ TF-IDF   │  │   BM25   │  │Embeddings│              │
│  │  Index   │  │  Index   │  │  Index   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   LLM    │  │   LLM    │  │   LLM    │              │
│  │Classifier│  │ Generator│  │  Editor  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend Architecture

### **Technology Stack**
- **Framework**: FastAPI (Python 3.10+)
- **LLM Provider**: OpenAI (GPT-4o-mini, text-embedding-3-small)
- **NLP Libraries**: Custom implementations for TF-IDF, BM25
- **Data Processing**: NumPy, regex, JSON
- **PDF Processing**: pdfplumber (for Streamlit interface)

### **Core Modules**

#### 1. **Orchestrator (`orchestrator.py`)**
The main pipeline coordinator that orchestrates the entire workflow:
- Coordinates all pipeline stages
- Manages configuration and environment setup
- Handles adaptive weight calculation for hybrid ranking
- Exports results in multiple formats (JSON, Markdown, ZIP)

#### 2. **Retrieval System**
Three complementary retrieval methods:

**a) TF-IDF Index (`retrieval_tfidf.py`)**
- Classic keyword-based retrieval
- Term frequency-inverse document frequency weighting
- Best for exact keyword matching

**b) BM25 Index (`retrieval_bm25.py`)**
- Probabilistic ranking function
- Strong baseline for textual relevance
- Handles term saturation better than TF-IDF

**c) Embedding Index (`retrieval_embed.py`)**
- Semantic similarity using OpenAI embeddings
- Captures meaning beyond keywords
- Requires API calls but provides deeper understanding

#### 3. **Profile Processing (`core/chunking.py`)**
- **Section Detection**: Automatically identifies resume sections (Summary, Experience, Projects, Skills, Education)
- **Intelligent Chunking**: Splits profile into overlapping chunks (default: 1200 chars, 200 char overlap)
- **Tokenization**: Preprocesses text with stopword removal
- **Chunk Metadata**: Each chunk includes section, text, tokens, and unique ID

#### 4. **Job Description Parsing**

**a) Rule-Based Parser (`agents/jd_parser_rules.py`)**
- Extracts must-have skills, nice-to-have skills, responsibilities, keywords
- Uses skill taxonomy for normalization
- Fast and deterministic

**b) LLM-Based Classifier (`agents/jd_classifier_llm.py`)**
- Optional LLM-powered refinement
- Better understanding of context and implicit requirements
- More accurate skill extraction from complex descriptions

#### 5. **Hybrid Ranking System (`core/ranker.py`)**
- **Multi-Method Fusion**: Combines TF-IDF, BM25, and embedding scores
- **Adaptive Weights**: Automatically adjusts weights based on enabled methods
- **Normalization**: Min-max normalization for fair score combination
- **Match Thresholding**: Configurable threshold for requirement matching
- **Score Calculation**:
  - Final score = (w_tfidf × score_tfidf) + (w_bm25 × score_bm25) + (w_embed × score_embed)
  - Default weights: BM25 (45%), TF-IDF (35%), Embeddings (20%)

#### 6. **Evidence Map Builder (`core/evidence.py`)**
- Links requirements to supporting profile chunks
- Extracts skills found in chunks using taxonomy
- Provides detailed scoring breakdown (final, TF-IDF, BM25 scores)
- Creates traceable evidence chain for each requirement

#### 7. **Generation System**

**a) LLM Generator (`agents/generator_llm.py`)**
- Generates resume bullets and cover letter
- Uses structured JSON prompts with few-shot examples
- Ensures all outputs reference evidence chunks
- Temperature: 0.2 (low for consistency)

**b) LLM Editor (`agents/editor_llm.py`)**
- Optional post-generation refinement
- Fixes validation issues while maintaining grounding
- Improves style and coherence

#### 8. **Validation & Grounding (`core/validators.py`)**
- **Content Validation**: Checks bullet length, evidence references, skill usage
- **Grounding Enforcement**: Ensures all claims are backed by evidence
- **Warning System**: Identifies potential issues without blocking generation
- **Taxonomy Verification**: Validates skills against known taxonomy

#### 9. **Export System (`core/export.py`)**
- JSON export for programmatic access
- Markdown export for human-readable output
- ZIP package containing all exports

### **API Endpoints**

#### `POST /run`
Main pipeline endpoint that processes job description and profile.

**Request Body:**
```json
{
  "job_description": "Full job description text...",
  "profile_text": "Candidate profile/resume text...",
  "company_name": "Optional company name",
  "role_title": "Optional role title",
  "use_tfidf": true,
  "use_bm25": true,
  "use_embeddings": false,
  "use_llm_jd_classifier": false,
  "use_llm_editor": true
}
```

**Response:**
```json
{
  "jd": {
    "company_name": "...",
    "role_title": "...",
    "must_have_skills": [...],
    "nice_to_have_skills": [...],
    "responsibilities": [...],
    "keywords": [...]
  },
  "match_report": {
    "match_score_overall": 85,
    "match_score_must": 90,
    "match_score_nice": 80,
    "matched_requirements": [...],
    "missing_requirements": [...]
  },
  "evidence_map": {...},
  "generation": {
    "resume_bullets": [...],
    "cover_letter": {...},
    "warnings": [...]
  },
  "validation": {
    "ok": true,
    "warnings": [...]
  }
}
```

#### `GET /health`
Health check endpoint for monitoring.

---

## 🎨 Frontend Architecture

### **Technology Stack**
- **Framework**: Next.js 16 (React 19)
- **Language**: TypeScript
- **UI Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **PDF Processing**: unpdf (serverless-compatible)

### **Key Components**

#### 1. **Request Form (`request-form.tsx`)**
- Job description input (textarea)
- Profile/resume input with **PDF upload support**
- Drag-and-drop PDF upload
- Company and role fields (optional)
- Configurable retrieval options (TF-IDF, BM25, Embeddings)
- Configurable generation options (LLM JD Classifier, LLM Editor)
- Sample data loader for quick testing

#### 2. **Match Summary (`match-summary.tsx`)**
- **Match Score Visualization**: 
  - Overall, Must-have, Nice-to-have scores
  - Color-coded progress bars (red <50%, amber 50-74%, green ≥75%)
  - Percentage badges
- **Skills Display**:
  - Must-have skills with count badges
  - Nice-to-have skills with accent colors
  - Responsibilities and keywords
- **Matched/Missing Requirements**: Visual badges

#### 3. **Generation Results (`generation-results.tsx`)**
- **Resume Bullets Section**:
  - Each bullet with skills used
  - Evidence chunk references
  - Item count badge
- **Cover Letter Section**:
  - Scrollable text area
  - Evidence chunk references
  - "Grounded" badge indicator
- **Validation Status**: OK/Issues badge
- **Warnings Display**: Alert component for validation warnings

#### 4. **Evidence Panel (`evidence-panel.tsx`)**
- **Fixed-height scrollable card** (matches Outputs card height)
- **Evidence Map Display**:
  - Requirements sorted by score
  - Matched/Missing badges
  - Score badges
  - Supporting chunks with:
    - Section labels
    - Score breakdowns (final, TF-IDF, BM25)
    - Chunk text (line-clamped)
    - Skills found in chunks
- **Footer**: Information about evidence derivation

### **PDF Upload Feature**

#### API Route: `/api/extract-pdf`
- Serverless function for PDF text extraction
- Uses `unpdf` library (serverless-compatible)
- Validates file type and size (10MB limit)
- Cleans extracted text (normalizes whitespace, fixes layout)
- Returns extracted text as JSON

#### Frontend Integration:
- Upload button with loading states
- Drag-and-drop support
- Real-time extraction feedback
- Automatic form population
- Character/line count display

---

## 🔄 Workflow & Pipeline

### **Complete Pipeline Flow**

```
1. INPUT PROCESSING
   ├─ Job Description Parsing
   │  ├─ Extract company/role (regex)
   │  ├─ Rule-based skill extraction
   │  └─ Optional: LLM-based refinement
   │
   └─ Profile Processing
      ├─ Section detection (Summary, Experience, etc.)
      ├─ Chunking (1200 chars, 200 overlap)
      └─ Tokenization & preprocessing

2. RETRIEVAL PHASE
   ├─ For each requirement:
   │  ├─ TF-IDF retrieval (if enabled)
   │  ├─ BM25 retrieval (if enabled)
   │  └─ Embedding retrieval (if enabled)
   │
   └─ Hybrid ranking
      ├─ Score normalization (min-max)
      ├─ Weighted combination
      └─ Top-K chunk selection

3. MATCHING & EVIDENCE
   ├─ Requirement matching (threshold-based)
   ├─ Evidence map construction
   │  ├─ Link requirements to chunks
   │  ├─ Extract skills from chunks
   │  └─ Calculate match scores
   │
   └─ Match report generation
      ├─ Overall score
      ├─ Must-have score
      ├─ Nice-to-have score
      └─ Matched/missing lists

4. GENERATION PHASE
   ├─ LLM Generation
   │  ├─ Resume bullets (evidence-grounded)
   │  ├─ Cover letter (tailored to JD)
   │  └─ Evidence chunk references
   │
   ├─ Validation
   │  ├─ Check bullet length
   │  ├─ Verify evidence references
   │  └─ Validate skill usage
   │
   └─ Optional: LLM Editing
      ├─ Fix validation issues
      ├─ Improve style
      └─ Maintain grounding

5. OUTPUT & EXPORT
   ├─ JSON export (full data)
   ├─ Markdown export (human-readable)
   └─ ZIP package (all exports)
```

### **Adaptive Configuration**

The system adapts to enabled retrieval methods:
- **Single method**: Lower threshold (0.30 max) for more lenient matching
- **Multiple methods**: Uses configured threshold (default 0.62)
- **Weight normalization**: Automatically normalizes weights when methods are disabled

---

## ✨ Key Features

### **1. Multi-Method Retrieval**
- **TF-IDF**: Fast keyword matching
- **BM25**: Better term saturation handling
- **Embeddings**: Semantic understanding
- **Hybrid Fusion**: Best of all methods

### **2. Evidence-Based Generation**
- All resume bullets reference specific profile chunks
- Cover letter grounded in evidence
- Transparent evidence map for verification
- Prevents hallucinations

### **3. Intelligent Profile Processing**
- Automatic section detection
- Smart chunking with overlap
- Skill extraction from chunks
- Taxonomy-based skill normalization

### **4. Flexible Configuration**
- Toggle retrieval methods on/off
- Optional LLM-based JD classification
- Optional LLM-based editing
- Adaptive thresholds and weights

### **5. Comprehensive Validation**
- Content validation (length, format)
- Grounding verification
- Skill taxonomy checking
- Warning system (non-blocking)

### **6. Modern User Interface**
- Clean, responsive design
- Real-time feedback
- PDF upload with drag-and-drop
- Visual score indicators
- Scrollable evidence maps
- Color-coded progress bars

### **7. Export Capabilities**
- JSON for programmatic access
- Markdown for human reading
- ZIP packages for distribution

---

## 🛠️ Technical Stack Summary

### **Backend**
- Python 3.10+
- FastAPI (REST API)
- OpenAI API (GPT-4o-mini, text-embedding-3-small)
- NumPy (vector operations)
- pdfplumber (PDF extraction for Streamlit)
- Pydantic (data validation)

### **Frontend**
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui (Radix UI)
- unpdf (PDF extraction)
- Lucide React (icons)

### **Data Formats**
- JSON (API communication, exports)
- Markdown (human-readable exports)
- YAML (skill taxonomy, configuration)

---

## 📊 Performance Characteristics

- **Retrieval Speed**: TF-IDF/BM25 are fast (milliseconds), embeddings require API calls
- **Generation Time**: ~5-15 seconds depending on LLM model and content length
- **Scalability**: Stateless API design allows horizontal scaling
- **Memory**: Efficient chunking keeps memory usage reasonable

---

## 🔒 Quality Assurance

- **Grounded Generation**: All outputs linked to evidence
- **Validation System**: Multi-layer validation prevents errors
- **Error Handling**: Graceful degradation when methods fail
- **Type Safety**: TypeScript on frontend, Pydantic on backend

---

## 🚀 Future Enhancements

Potential improvements:
- Caching for repeated queries
- Batch processing for multiple JDs
- Custom skill taxonomy upload
- Export to DOCX/PDF formats
- Multi-language support
- Advanced analytics dashboard

---

## 📝 Conclusion

The **Generative Resume and Cover Letter Assistant** demonstrates a production-ready approach to AI-powered content generation with strong emphasis on:
- **Transparency**: Clear evidence mapping
- **Reliability**: Multi-method retrieval and validation
- **Flexibility**: Configurable pipeline
- **User Experience**: Modern, intuitive interface

The system successfully combines traditional NLP techniques (TF-IDF, BM25) with modern AI (embeddings, LLMs) to create a robust, grounded generation pipeline.

---

*Document generated for presentation purposes*
*Last updated: 2024*

