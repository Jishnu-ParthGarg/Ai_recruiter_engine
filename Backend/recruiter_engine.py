from pathlib import Path
from functools import lru_cache
import json
import re
from typing import Dict, Set

# =====================================================
# CONFIG
# =====================================================

PROFILE_WEIGHT = 0.20
JD_WEIGHT = 0.80

BASE_DIR = Path(__file__).resolve().parent

DATA_PATHS = [
    BASE_DIR / "scored_candidates.json",
    BASE_DIR.parent / "scored_candidates.json",
]

# =====================================================
# SKILL TAXONOMY
# =====================================================

MASTER_SKILLS = {
    "python", "java", "javascript", "react", "html", "css",
    "machine learning", "deep learning", "statistics",
    "rag", "llm", "langchain", "faiss", "pinecone",
    "tensorflow", "pytorch", "scikit-learn",
    "nlp", "opencv", "yolo"
}

ALIASES = {
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "llms": "llm",
    "vector db": "vector database",
}

SEMANTIC_MAP = {
    "machine learning": {"tensorflow", "pytorch", "scikit-learn", "deep learning"},
    "statistics": {"pandas", "numpy", "data science"},
    "rag": {"langchain", "faiss", "pinecone"},
    "frontend": {"react", "javascript", "html", "css"},
}

# =====================================================
# LOAD DATA
# =====================================================

@lru_cache(maxsize=1)
def load_candidates():
    for path in DATA_PATHS:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                data = data.get("data", [])

            return data

    raise RuntimeError(f"Dataset not found in: {DATA_PATHS}")

# =====================================================
# JD PARSER
# =====================================================

def extract_jd_requirements(job_description: str) -> Set[str]:

    jd = (job_description or "").lower()
    jd = re.sub(r"[^a-z0-9+#.\s]", " ", jd)

    tokens = set(jd.split())
    detected = set()

    for skill in MASTER_SKILLS:
        normalized = ALIASES.get(skill, skill)

        if " " in skill:
            if skill in jd:
                detected.add(normalized)
        else:
            if skill in tokens:
                detected.add(normalized)

    return detected

# =====================================================
# JD MATCHER
# =====================================================

def calculate_jd_score(candidate: Dict, requirements: Set[str]):

    if not requirements:
        return 0.0, [], []

    skills = set(map(str.lower, candidate.get("skill_names", [])))

    matched = set()

    matched |= skills & requirements

    for req in requirements:
        if req in SEMANTIC_MAP and skills & SEMANTIC_MAP[req]:
            matched.add(req)

    if candidate.get("has_python") and "python" in requirements:
        matched.add("python")

    if candidate.get("has_ml") and any(x in requirements for x in ["machine learning", "deep learning"]):
        matched.add("machine learning")

    if candidate.get("has_retrieval_experience") and "rag" in requirements:
        matched.add("rag")

    missing = requirements - matched

    score = (len(matched) / max(len(requirements), 1)) * 100

    return round(score, 2), list(matched), list(missing)

# =====================================================
# MAIN ENGINE (FINAL FIXED CONTRACT)
# =====================================================

def get_top_candidates(job_description: str, top_k: int = 10):

    candidates = load_candidates()
    jd_text = (job_description or "").lower()

    requirements = extract_jd_requirements(job_description)

    # fallback prevents empty JD crash
    if not requirements:
        requirements = {"python", "javascript"}

    ranked = []

    for c in candidates:

        profile = float(c.get("final_score", 0) or 0)
        profile = min(profile, 100)

        jd_score, matched, missing = calculate_jd_score(c, requirements)

        role_boost = 0
        skills = set(map(str.lower, c.get("skill_names", [])))

        if ("frontend" in jd_text or "react" in jd_text) and "react" in skills:
            role_boost += 10

        if ("machine learning" in jd_text or "data science" in jd_text) and c.get("has_ml"):
            role_boost += 10

        if ("rag" in jd_text or "llm" in jd_text) and c.get("has_retrieval_experience"):
            role_boost += 10

        final_score = (jd_score ** 1.1) * JD_WEIGHT + profile * PROFILE_WEIGHT + role_boost

        ranked.append({
            "candidate_id": c.get("candidate_id", ""),
            "current_title": c.get("current_title", "Unknown Title"),
            "years_experience": float(c.get("years_experience", 0)),
            "location": c.get("location", "N/A"),

            "skills": c.get("skill_names", []),

            "jd_score": jd_score,
            "profile_score": profile,
            "final_score": round(final_score, 2),

            "matched_skills": matched,
            "missing_skills": missing,

            "explanation": f"Matched {len(matched)}/{len(requirements)} skills"
        })

    ranked.sort(key=lambda x: x["final_score"], reverse=True)

    return ranked[:top_k]