from pathlib import Path
from functools import lru_cache
import json
import re
from typing import Dict, Set, List

# =====================================================
# CONFIG
# =====================================================

PROFILE_WEIGHT = 0.25
JD_WEIGHT = 0.75

BASE_DIR = Path(__file__).resolve().parent

DATA_PATHS = [
    BASE_DIR / "scored_candidates.json",
    BASE_DIR.parent / "scored_candidates.json",
]

# =====================================================
# ROLE INTELLIGENCE (🔥 KEY FIX)
# =====================================================

ROLE_MAP = {
    "frontend": {"react", "javascript", "html", "css", "ui", "ux"},
    "backend": {"python", "java", "fastapi", "django", "node", "api"},
    "ml": {"machine learning", "deep learning", "nlp", "llm", "pytorch", "tensorflow"},
    "data": {"statistics", "pandas", "numpy", "sql"},
}

# =====================================================
# MASTER SKILLS
# =====================================================

MASTER_SKILLS = set().union(*ROLE_MAP.values()).union({
    "rag", "langchain", "faiss", "pinecone",
    "opencv", "yolo", "scikit-learn"
})

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

    raise RuntimeError("scored_candidates.json not found")

# =====================================================
# ROLE DETECTION (🔥 CRITICAL)
# =====================================================

def detect_role(jd: str) -> str:

    jd = jd.lower()

    if any(k in jd for k in ["react", "frontend", "ui", "html", "css"]):
        return "frontend"

    if any(k in jd for k in ["ml", "machine learning", "ai", "model", "data science"]):
        return "ml"

    if any(k in jd for k in ["api", "backend", "server", "django", "fastapi"]):
        return "backend"

    if any(k in jd for k in ["sql", "analytics", "pandas", "statistics"]):
        return "data"

    return "general"

# =====================================================
# JD PARSER
# =====================================================

def extract_jd_requirements(jd: str) -> Set[str]:

    jd = (jd or "").lower()
    jd = re.sub(r"[^a-z0-9+#.\s]", " ", jd)

    detected = set()

    for skill in MASTER_SKILLS:
        if skill in jd:
            detected.add(skill)

    return detected

# =====================================================
# SCORING ENGINE
# =====================================================

def calculate_score(candidate: Dict, reqs: Set[str], role: str):

    skills = set(map(str.lower, candidate.get("skill_names", [])))

    matched = skills & reqs

    # role boost (🔥 FIXED LOGIC)
    role_boost = 0

    if role == "frontend" and skills & ROLE_MAP["frontend"]:
        role_boost += 15

    if role == "ml" and candidate.get("has_ml"):
        role_boost += 15

    if role == "backend" and "python" in skills:
        role_boost += 10

    if role == "data" and "statistics" in skills:
        role_boost += 10

    jd_score = (len(matched) / max(len(reqs), 1)) * 100

    return jd_score, list(matched), role_boost

# =====================================================
# MAIN ENGINE (FIXED + DIVERSE OUTPUT)
# =====================================================

def get_top_candidates(job_description: str, top_k: int = 10):

    candidates = load_candidates()

    role = detect_role(job_description)
    reqs = extract_jd_requirements(job_description)

    ranked = []

    for c in candidates:

        profile = float(c.get("final_score", 0) or 0)
        profile = min(profile, 100)

        jd_score, matched, role_boost = calculate_score(c, reqs, role)

        final = (
            jd_score * JD_WEIGHT +
            profile * PROFILE_WEIGHT +
            role_boost
        )

        ranked.append({
            "candidate_id": c.get("candidate_id", ""),
            "current_title": c.get("current_title", "Unknown Title"),
            "years_experience": c.get("years_experience", 0),
            "location": c.get("location", "N/A"),

            # 🔥 FRONTEND FIX (IMPORTANT)
            "skills": c.get("skill_names", []),
            "skill_names": c.get("skill_names", []),

            "jd_score": round(jd_score, 2),
            "profile_score": round(profile, 2),
            "final_score": round(final, 2),

            "matched_skills": matched,

            "explanation": f"{role.upper()} match: {len(matched)} skills"
        })

    ranked.sort(key=lambda x: x["final_score"], reverse=True)

    # diversity fix (prevents same candidates repeating)
    seen = set()
    output = []

    for r in ranked:
        if r["candidate_id"] not in seen:
            output.append(r)
            seen.add(r["candidate_id"])

        if len(output) == top_k:
            break

    return output