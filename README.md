# 🤖 AI Recruiter System

An AI-powered candidate ranking platform that turns a job description into an explainable, ranked shortlist — combining LLM-based requirement extraction with multi-signal candidate scoring.

Unlike traditional ATS systems that rely on keyword filtering alone, this system combines:

- 🧠 LLM-powered job description understanding
- 📊 Multi-dimensional candidate evaluation
- 👥 Behavioral and recruiter-interaction signals
- ⚖️ Business-rule-aware ranking (soft penalties, not hard rejections)
- 🔍 Explainable, recruiter-readable recommendations

---

## 🔗 Live Demo

| | |
|---|---|
| **Frontend** | [ai-recruiter-engine.vercel.app](https://ai-recruiter-engine.vercel.app/) |
| **Backend API** | [test2-ox8y.onrender.com](https://test2-ox8y.onrender.com) |
| **API Docs** | [test2-ox8y.onrender.com/docs](https://test2-ox8y.onrender.com/docs) |

---

## Table of Contents

- [How It Works](#-how-it-works)
- [Features](#-features)
- [Ranking Methodology](#-ranking-methodology)
- [Fallback Strategy](#-built-in-fallback-strategy)
- [Results & Performance](#-results--performance)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Running Locally](#-running-locally)
- [API Reference](#-api-reference)
- [Submission Assets](#-submission-assets)

---

## ⚙️ How It Works

```text
Job Description
      │
      ▼
LLM Requirement Extraction   (skills, role, seniority, domain)
      │
      ▼
Candidate Feature Extraction (technical, behavioral, logistics, career, risk)
      │
      ▼
Candidate Scoring + Business Rules
      │
      ▼
JD Matching + Final Ranking
      │
      ▼
Explainability Layer  →  FastAPI  →  React Frontend
```

1. **Recruiter submits a job description.**
2. **LLM extracts requirements** — skills, role, seniority, domain.
3. **Every candidate is evaluated** across technical, behavioral, logistics, career, and risk signals.
4. **JD matching** computes skill overlap, experience match, leadership match, and role alignment.
5. **Ranking** combines profile score + JD match score − business penalties.
6. **Explainability generation** returns a recruiter-readable rationale for each result.

---

## ✨ Features

### 🧠 AI-Powered Job Description Understanding

Uses **Llama 3.1 via Groq** to extract recruiter intent — technical skills, role requirements, seniority, domain expertise, and leadership expectations.

**Example**

> Input: *"Senior Retrieval Engineer with Python and Vector Search"*
> Extracted: Python · Machine Learning · Retrieval Systems · Vector Search · Information Retrieval · Leadership Experience

### 📊 Multi-Signal Candidate Evaluation

| Category | Signals |
|---|---|
| 💻 Technical | Python/ML/retrieval/vector-DB expertise, leadership indicators, skill diversity |
| 👥 Behavioral | Open-to-work status, recruiter response rate, interview completion, recruiter engagement |
| 📅 Logistics | Notice period, availability |
| 💼 Career | Years of experience, current role, industry, career progression |
| 🚩 Risk | Honeypot detection, consulting-only profiles, suspicious patterns |

### 🔍 Explainable AI Ranking

Every candidate gets a plain-language rationale, e.g.:

> *"Candidate demonstrates strong technical fit, high recruiter engagement, good alignment with the target role, and favorable notice period."*

### ⚖️ Business Rule Engine

Applies **soft penalties** rather than hard rejections (e.g. for consulting-only profiles or weak role alignment), preserving candidate diversity in the shortlist.

---

## 🎯 Ranking Methodology

```text
Final Score =
    Technical Score
  + Behavioral Score
  + Logistics Score
  + Role Alignment Score
  + JD Matching Score
  − Honeypot Penalty
  − Consulting Penalty
```

| Component | Measures |
|---|---|
| **Technical Score** | Experience, ML/retrieval/vector-DB expertise, leadership |
| **Behavioral Score** | Recruiter response rate, open-to-work signal, interview completion, recruiter saves |
| **Logistics Score** | Notice period, availability |
| **Role Alignment Score** | Candidate title/experience vs. target role (e.g. ML Engineer, AI Engineer, NLP Engineer, Search Engineer, Applied Scientist) |
| **Penalty Score** | Honeypot detection, consulting penalties, weak alignment, low experience |

---

## 🛡️ Built-in Fallback Strategy

The system degrades gracefully instead of failing outright:

| Situation | Behavior |
|---|---|
| ✅ LLM extraction succeeds | Full requirement extraction |
| ⚠️ LLM unavailable | Keyword-based extraction fallback |
| ⚠️ Generic JD (e.g. "Frontend Developer") | Role → baseline-skills mapping |
| ❌ Nothing extracted | General candidate ranking, flagged in the UI |

---

## 📈 Results & Performance

**Dataset:** 61,579 candidate profiles, pre-scored on technical, behavioral, logistics, and role-fit dimensions.

**Example query:** *"Senior Retrieval Engineer with Python and Vector Search"*

| Candidate | Final Score |
|---|---|
| CAND_0002025 | 135.95 |
| CAND_0025640 | 133.80 |
| CAND_0046064 | 132.45 |
| CAND_0072660 | 131.55 |
| CAND_0079387 | 130.45 |

**Runtime**

| Stage | Complexity |
|---|---|
| Feature extraction | O(N) |
| Candidate scoring | O(N) |
| Business rules | O(N) |
| Ranking | O(N log N) |

Average end-to-end response time (JD parsing + matching + ranking): **< 1 second**, running on CPU only — no GPU required, standard laptop hardware, low memory overhead.

---

## 🛠️ Tech Stack

**Backend** — Python, FastAPI, Groq API (Llama 3.1), JSON/Gzip storage
`json · gzip · re · typing · pathlib · fastapi · uvicorn · pydantic`

**Frontend** — React, Vite, Axios

**Deployment** — Render (backend), Vercel (frontend)

---

## 📂 Project Structure

```text
Backend/
├── ranked.py
├── recruiter_engine.py
├── jd_parser.py
├── main.py
├── models.py
├── scored_candidates.json
└── requirements.txt

Frontend/
├── src/
│   ├── App.jsx
│   ├── App.css
│   └── components/
├── package.json
└── vite.config.js
```

---

## 🚀 Running Locally

### Backend

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file in `Backend/`:

```env
GROQ_API_KEY=your_groq_api_key
```

Get a free key at [console.groq.com/keys](https://console.groq.com/keys) — no credit card required.

```bash
uvicorn main:app --reload --port 8080
```

- Interactive API docs: `http://127.0.0.1:8080/docs`
- Health check: `http://127.0.0.1:8080/health`

### Frontend

```bash
cd Frontend
npm install
```

Create a `.env` file in `Frontend/`:

```env
VITE_BACKEND_URL=http://127.0.0.1:8080
```

```bash
npm run dev
```

---

## 📡 API Reference

### `POST /rank_candidates`

**Request**

```json
{
  "job_description": "Backend developer with Python, SQL, and API experience",
  "top_k": 5,
  "use_llm": true
}
```

**Response**

```json
{
  "success": true,
  "count": 5,
  "used_llm": true,
  "generic_ranking": false,
  "top_candidates": [
    {
      "candidate_id": "CAND_0000001",
      "current_title": "backend engineer",
      "years_experience": 6.9,
      "location": "toronto",
      "skills": ["python", "sql", "..."],
      "jd_score": 66.67,
      "profile_score": 75,
      "final_score": 79.17,
      "matched_skills": ["python", "sql"],
      "missing_skills": ["api"]
    }
  ]
}
```

### `GET /health`

Returns whether the Groq client initialized successfully — useful for confirming the API key is configured correctly in production.

---

## 📦 Submission Assets

- `ranked.py`
- `recruiter_engine.py`
- `jd_parser.py`
- FastAPI backend
- React frontend
- `scored_candidates.json`
- `top_candidates.json`
- `submission.csv`

---

## 🌟 Key Strengths

✅ Explainable AI ranking · ✅ Multi-signal candidate evaluation · ✅ Business rule engine · ✅ Soft filtering strategy · ✅ LLM-powered JD understanding · ✅ Full-stack implementation · ✅ Production-style architecture

---
