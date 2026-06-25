import re


def extract_jd_requirements(job_description: str):
    """
    Extracts important requirements from the Job Description.
    Returns a dictionary of detected skills/requirements.
    """

    if not job_description:
        job_description = ""

    jd = job_description.lower()

    # Remove punctuation
    jd = re.sub(r"[^\w\s]", " ", jd)

    requirements = {
        "python": False,
        "ml": False,
        "retrieval": False,
        "leadership": False,
    }

    # -------------------------
    # Python
    # -------------------------
    python_keywords = [
        "python",
    ]

    # -------------------------
    # Machine Learning / AI
    # -------------------------
    ml_keywords = [
        "machine learning",
        "ml",
        "artificial intelligence",
        "ai",
        "deep learning",
        "neural network",
        "tensorflow",
        "pytorch",
        "scikit",
    ]

    # -------------------------
    # Retrieval / Search / Ranking
    # -------------------------
    retrieval_keywords = [
        "retrieval",
        "retrieval augmented generation",
        "rag",
        "ranking",
        "search",
        "semantic search",
        "vector database",
        "vector search",
        "recommendation",
    ]

    # -------------------------
    # Leadership
    # -------------------------
    leadership_keywords = [
        "lead",
        "team lead",
        "leadership",
        "manager",
        "management",
        "mentor",
        "mentoring",
    ]

    requirements["python"] = any(k in jd for k in python_keywords)
    requirements["ml"] = any(k in jd for k in ml_keywords)
    requirements["retrieval"] = any(k in jd for k in retrieval_keywords)
    requirements["leadership"] = any(k in jd for k in leadership_keywords)

    return requirements