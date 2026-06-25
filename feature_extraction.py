# feature_extraction.py

import json

# ==========================================
# CONSULTING COMPANIES
# ==========================================

CONSULTING_COMPANIES = {
    "tcs",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "hcl",
    "tech mahindra",
    "mindtree",
    "ltimindtree"
}

# ==========================================
# RETRIEVAL / RECOMMENDATION KEYWORDS
# ==========================================

RETRIEVAL_KEYWORDS = {
    "retrieval",
    "ranking",
    "search",
    "recommendation",
    "recommendations",
    "recommender",
    "matching",
    "personalization",
    "vector search",
    "information retrieval",
    "embeddings",
    "semantic search",
    "learning to rank"
}

VECTOR_DB_SKILLS = {
    "pinecone",
    "weaviate",
    "milvus",
    "qdrant",
    "faiss",
    "elasticsearch",
    "opensearch"
}

# ==========================================
# ML SKILLS
# ==========================================

ML_KEYWORDS = {
    "machine learning",
    "deep learning",
    "nlp",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "computer vision",
    "speech recognition",
    "gans",
    "lora",
    "fine-tuning llms"
}

# ==========================================
# PYTHON STACK
# ==========================================

PYTHON_RELATED = {
    "python",
    "flask",
    "django",
    "fastapi",
    "numpy",
    "pandas",
    "scikit-learn"
}

# ==========================================
# FEATURE EXTRACTION
# ==========================================

def extract_features(candidate):

    features = {}

    # --------------------------------------
    # Candidate ID
    # --------------------------------------

    features["candidate_id"] = candidate.get(
        "candidate_id",
        ""
    )

    # --------------------------------------
    # Profile
    # --------------------------------------

    profile = candidate.get(
        "profile",
        {}
    )

    features["years_experience"] = profile.get(
        "years_of_experience",
        0
    )

    features["current_title"] = profile.get(
        "current_title",
        ""
    ).lower()

    features["industry"] = profile.get(
        "current_industry",
        ""
    ).lower()

    # FIXED FIELD NAME
    features["location"] = profile.get(
        "location",
        ""
    ).lower()

    # --------------------------------------
    # Skills
    # --------------------------------------

    skills = candidate.get(
        "skills",
        []
    )

    skill_names = set()

    for skill in skills:

        skill_name = skill.get(
            "name",
            ""
        ).lower().strip()

        if skill_name:
            skill_names.add(
                skill_name
            )

    features["skill_names"] = list(
        skill_names
    )

    features["has_python"] = any(
        skill in skill_names
        for skill in PYTHON_RELATED
    )

    features["has_ml"] = bool(
        ML_KEYWORDS & skill_names
    )

    # --------------------------------------
    # Career History
    # --------------------------------------

    career_history = candidate.get(
        "career_history",
        []
    )

    career_text = ""

    consulting_only = True

    for job in career_history:

        description = job.get(
            "description",
            ""
        ).lower()

        company = job.get(
            "company",
            ""
        ).lower()

        title = job.get(
            "title",
            ""
        ).lower()

        career_text += (
            description
            + " "
            + title
            + " "
        )

        if (
            company
            and company not in
            CONSULTING_COMPANIES
        ):
            consulting_only = False

    features[
        "consulting_only"
    ] = consulting_only

       # --------------------------------------
    # Retrieval Experience
    # --------------------------------------

    retrieval_flag = any(
        keyword in career_text
        for keyword in RETRIEVAL_KEYWORDS
    )

    vector_db_flag = any(
        skill in skill_names
        for skill in VECTOR_DB_SKILLS
    )

    features["has_retrieval_experience"] = (
        retrieval_flag or vector_db_flag
    )

    # Count retrieval/vector DB skills

    retrieval_skill_count = sum(
        1
        for skill in skill_names
        if skill in VECTOR_DB_SKILLS
    )

    features["retrieval_skill_count"] = (
        retrieval_skill_count
    )

    # --------------------------------------
    # Leadership Signals
    # --------------------------------------

    leadership_keywords = [
        "led",
        "lead",
        "team lead",
        "managed",
        "manager",
        "mentored",
        "mentor",
        "leadership"
    ]

    features["has_leadership"] = any(
        keyword in career_text
        for keyword in leadership_keywords
    )
    
    # --------------------------------------
    # Redrob Signals
    # --------------------------------------

    signals = candidate.get(
        "redrob_signals",
        {}
    )

    features["open_to_work"] = signals.get(
        "open_to_work_flag",
        False
    )

    features["response_rate"] = signals.get(
        "recruiter_response_rate",
        0
    )

    features["notice_period"] = signals.get(
        "notice_period_days",
        999
    )

    features["saved_by_recruiters"] = signals.get(
        "saved_by_recruiters_30d",
        0
    )

    features[
        "interview_completion"
    ] = signals.get(
        "interview_completion_rate",
        0
    )

    return features


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    from load_candidates import candidates

    print(
        "Extracting features..."
    )

    candidate_features = []

    for candidate in candidates:

        features = extract_features(
            candidate
        )

        candidate_features.append(
            features
        )

    print(
        "Feature extraction completed."
    )

    print(
        "Total candidates processed:",
        len(candidate_features)
    )

    with open(
        "candidate_features.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            candidate_features,
            f,
            indent=2
        )

    print(
        "Features saved successfully."
    )

    print(
        "\nSample Candidate:\n"
    )

    if candidate_features:

        print(
            candidate_features[0]
        )