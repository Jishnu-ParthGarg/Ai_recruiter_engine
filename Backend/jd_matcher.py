from typing import Dict


def calculate_jd_score(candidate: Dict, requirements: Dict):

    score = 0

    skills = [
        skill.lower()
        for skill in candidate.get("skill_names", [])
    ]

    title = candidate.get("current_title", "").lower()

    # Python
    if requirements["python"]:
        if "python" in skills:
            score += 10

    # Machine Learning
    if requirements["ml"]:
        ml_skills = {
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "ai",
        }

        if any(skill in ml_skills for skill in skills):
            score += 10

    # Retrieval / Search
    if requirements["retrieval"]:
        retrieval_skills = {
            "retrieval",
            "rag",
            "vector db",
            "vector database",
            "search",
            "ranking",
            "recommendation systems",
        }

        if any(skill in retrieval_skills for skill in skills):
            score += 15

    # Leadership
    if requirements["leadership"]:
        if (
            "lead" in title
            or "manager" in title
            or "architect" in title
        ):
            score += 5

    return score