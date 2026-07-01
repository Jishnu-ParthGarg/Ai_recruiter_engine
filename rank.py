import gzip
import json
import csv
import os
from typing import Dict, List


# =========================================================
# CREATE REQUIRED FOLDERS (AUTO SETUP)
# =========================================================

os.makedirs("data", exist_ok=True)


# =========================================================
# CONFIG
# =========================================================

PYTHON_STACK = {"python"}
ML_KEYWORDS = {"machine learning", "ml", "ai"}
RETRIEVAL_KEYWORDS = {"retrieval", "search", "vector", "embedding"}
CONSULTING_KEYWORDS = {"consulting", "strategy", "mckinsey", "bcg", "bain"}


# =========================================================
# DATA LOADER
# =========================================================

def load_candidates(path: str) -> List[Dict]:
    data = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


# =========================================================
# HELPERS
# =========================================================

def build_career_text(career):
    return " ".join(
        (job.get("title", "") + " " + job.get("description", "")).lower()
        for job in career
    )


def has_retrieval(skills, text):
    return bool(skills & RETRIEVAL_KEYWORDS) or any(
        k in text for k in RETRIEVAL_KEYWORDS
    )


def has_leadership(text):
    return any(x in text for x in ["lead", "manager", "head", "principal"])


def is_consulting_only(career):
    return all(
        any(k in str(job).lower() for k in CONSULTING_KEYWORDS)
        for job in career
    )


def count_retrieval_skills(skills):
    return len(skills & RETRIEVAL_KEYWORDS)


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def extract_features(candidate: Dict) -> Dict:

    profile = candidate.get("profile", {})

    skills = {
        s.get("name", "").lower().strip()
        for s in candidate.get("skills", [])
    }

    career = candidate.get("career_history", [])
    career_text = build_career_text(career)

    return {
        "candidate_id": candidate.get("candidate_id"),

        "years_experience": profile.get("years_of_experience", 0),
        "current_title": profile.get("current_title", "").lower(),
        "industry": profile.get("current_industry", "").lower(),
        "location": profile.get("location", "").lower(),

        "skills": list(skills),

        "has_python": bool(skills & PYTHON_STACK),
        "has_ml": bool(skills & ML_KEYWORDS),
        "has_retrieval": has_retrieval(skills, career_text),
        "retrieval_skill_count": count_retrieval_skills(skills),

        "has_leadership": has_leadership(career_text),
        "consulting_only": is_consulting_only(career),
    }


# =========================================================
# SCORING ENGINE
# =========================================================

def technical_score(c):
    score = 0
    if c["has_python"]:
        score += 10
    if c["has_ml"]:
        score += 15
    if c["has_retrieval"]:
        score += 15
    return score


def behavioral_score(c):
    return 20 if c["has_leadership"] else 10


def logistics_score(c):
    return 15 if c["years_experience"] >= 3 else 10


def role_score(c):
    score = 0
    if c["retrieval_skill_count"] > 2:
        score += 10
    if c["years_experience"] >= 3:
        score += 10
    return score


def penalties(c):
    return 15 if c["consulting_only"] else 0


def score_candidate(c: Dict) -> Dict:

    tech = technical_score(c)
    beh = behavioral_score(c)
    log = logistics_score(c)
    role = role_score(c)
    pen = penalties(c)

    final = tech + beh + log + role - pen

    return {
        **c,
        "technical_score": tech,
        "behavioral_score": beh,
        "logistics_score": log,
        "role_score": role,
        "penalty": pen,
        "final_score": round(final, 2)
    }


# =========================================================
# JD MATCHING
# =========================================================

def parse_jd(jd: str) -> Dict:
    jd = jd.lower()
    return {
        "python": "python" in jd,
        "ml": any(x in jd for x in ["ml", "machine learning", "ai"]),
        "retrieval": any(x in jd for x in ["retrieval", "search", "vector"]),
        "leadership": any(x in jd for x in ["lead", "manager", "principal"])
    }


def jd_score(c: Dict, req: Dict) -> int:
    score = 0

    if req["python"] and c["has_python"]:
        score += 10
    if req["ml"] and c["has_ml"]:
        score += 10
    if req["retrieval"] and c["has_retrieval"]:
        score += 10
    if req["leadership"] and c["has_leadership"]:
        score += 5

    return score


# =========================================================
# EXPLAINABILITY
# =========================================================

def explain(c: Dict) -> str:

    parts = []

    tech = []
    if c["has_python"]:
        tech.append("Python(+10)")
    if c["has_ml"]:
        tech.append("ML(+15)")
    if c["has_retrieval"]:
        tech.append("Retrieval(+15)")

    if tech:
        parts.append("Tech[" + ", ".join(tech) + "]")

    parts.append(f"Exp[{c['years_experience']} yrs]")

    if c["has_leadership"]:
        parts.append("Leadership[Yes(+20)]")

    parts.append(f"RoleScore[{c['role_score']}]")
    parts.append(f"Penalty[-{c['penalty']}]")
    parts.append(f"Final[{c['final_score']}]")

    return " | ".join(parts)


# =========================================================
# RANKING ENGINE
# =========================================================

def rank_candidates(candidates: List[Dict], jd: str, top_k: int = 100):

    req = parse_jd(jd)
    ranked = []

    for c in candidates:

        c = score_candidate(c)
        c["jd_score"] = jd_score(c, req)
        c["final_score"] += c["jd_score"]
        c["explanation"] = explain(c)

        ranked.append(c)

    ranked.sort(key=lambda x: x["final_score"], reverse=True)
    return ranked[:top_k]


# =========================================================
# OUTPUT (DATA FOLDER FIXED)
# =========================================================

def save_outputs(scored, ranked):

    with open("data/scored_candidates.json", "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=2)

    with open("data/top_candidates.json", "w", encoding="utf-8") as f:
        json.dump(ranked, f, indent=2)


def generate_submission(ranked):

    with open("data/submission.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["candidate_id", "rank", "score", "reason"])

        for i, c in enumerate(ranked, 1):
            writer.writerow([
                c["candidate_id"],
                i,
                c["final_score"],
                c["explanation"]
            ])


# =========================================================
# MAIN PIPELINE
# =========================================================

if __name__ == "__main__":

    raw = load_candidates("data/candidates.jsonl.gz")

    scored = [
        score_candidate(extract_features(c))
        for c in raw
    ]

    jd = "Senior Retrieval Engineer with Python and Vector Search"
    ranked = rank_candidates(scored, jd)

    save_outputs(scored, ranked)
    generate_submission(ranked)