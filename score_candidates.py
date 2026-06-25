# score_candidates.py

import json
import re

# ==========================================
# CONFIGURATION
# ==========================================

MIN_FINAL_SCORE = 25
MAX_HONEYPOT_PENALTY = 25
MIN_ROLE_SCORE = -50

# ==========================================
# TEXT CLEANING
# ==========================================

def clean_text(text):
    return re.sub(
        r"[^a-z0-9 ]",
        "",
        str(text).lower()
    ).strip()

# ==========================================
# TECHNICAL SCORE
# ==========================================

def technical_score(features):

    score = 0

    years = features.get(
        "years_experience",
        0
    )

    if 5 <= years <= 9:
        score += 20

    elif 4 <= years < 5:
        score += 15

    elif 9 < years <= 12:
        score += 12

    elif years > 12:
        score += 5

    if features.get(
        "has_ml",
        False
    ):
        score += 15

    if features.get(
        "has_retrieval_experience",
        False
    ):
        score += 25

    score += min(
        features.get(
            "retrieval_skill_count",
            0
        ) * 2,
        10
    )

    if features.get(
        "has_leadership",
        False
    ):
        score += 5

    return score

# ==========================================
# BEHAVIORAL SCORE
# ==========================================

def behavioral_score(features):

    score = 0

    if features.get(
        "open_to_work",
        False
    ):
        score += 5

    response_rate = features.get(
        "response_rate",
        0
    )

    if response_rate >= 0.8:
        score += 10

    elif response_rate >= 0.5:
        score += 7

    elif response_rate >= 0.3:
        score += 4

    interview_completion = features.get(
        "interview_completion",
        0
    )

    if interview_completion >= 0.8:
        score += 5

    saved = features.get(
        "saved_by_recruiters",
        0
    )

    if saved >= 10:
        score += 5

    elif saved >= 5:
        score += 3

    return score

# ==========================================
# LOGISTICS SCORE
# ==========================================

def logistics_score(features):

    score = 0

    notice = features.get(
        "notice_period",
        999
    )

    if notice <= 30:
        score += 5

    elif notice <= 60:
        score += 3

    return score

# ==========================================
# ROLE ALIGNMENT
# ==========================================

def role_alignment_score(features):

    title = clean_text(
        features.get(
            "current_title",
            ""
        )
    )

    years = features.get(
        "years_experience",
        0
    )

    relevant = [
        "ml engineer",
        "machine learning engineer",
        "ai engineer",
        "nlp engineer",
        "search engineer",
        "research engineer",
        "applied scientist",
        "data scientist",
        "recommendation"
    ]

    partial = [
        "software engineer",
        "backend engineer",
        "data engineer"
    ]

    irrelevant = [
        "marketing",
        "customer support",
        "content writer"
    ]

    if any(
        role in title
        for role in irrelevant
    ):
        return -50

    if any(
        role in title
        for role in relevant
    ):
        return 15 + min(
            years * 0.5,
            5
        )

    if any(
        role in title
        for role in partial
    ):
        return 8

    return 0

# ==========================================
# HONEYPOT DETECTION
# ==========================================

def honeypot_penalty(features):

    penalty = 0

    years = features.get(
        "years_experience",
        0
    )

    title = clean_text(
        features.get(
            "current_title",
            ""
        )
    )

    skills = features.get(
        "skill_names",
        []
    )

    if (
        years < 3 and
        (
            "principal" in title or
            "director" in title
        )
    ):
        penalty += 25

    if (
        years > 15 and
        (
            "intern" in title or
            "junior" in title
        )
    ):
        penalty += 25

    if len(skills) > 40:
        penalty += 10

    return penalty

# ==========================================
# CONSULTING PENALTY
# ==========================================

def consulting_penalty(features):

    if features.get(
        "consulting_only",
        False
    ):
        return 10

    return 0

# ==========================================
# FINAL SCORE
# ==========================================

def calculate_final_score(features):

    tech = technical_score(
        features
    )

    behavior = behavioral_score(
        features
    )

    logistics = logistics_score(
        features
    )

    role = role_alignment_score(
        features
    )

    honeypot = honeypot_penalty(
        features
    )

    consulting = consulting_penalty(
        features
    )

    final = (
        tech +
        behavior +
        logistics +
        role -
        honeypot -
        consulting
    )

    return {

        # Preserve all extracted features
        **features,

        # Add scoring outputs
        "technical_score":
            tech,

        "behavioral_score":
            behavior,

        "logistics_score":
            logistics,

        "role_score":
            role,

        "honeypot_penalty":
            honeypot,

        "consulting_penalty":
            consulting,

        "final_score":
            round(final, 2)
    }



# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print("Loading candidate features...")

    with open(
        "candidate_features.json",
        "r",
        encoding="utf-8"
    ) as f:

        candidate_features = json.load(f)

    print(
        "Total candidates loaded:",
        len(candidate_features)
    )

    scored_candidates = []
    rejected_candidates = []

    summary = {
        "total_candidates":
            len(candidate_features),

        "selected_candidates": 0,
        "rejected_candidates": 0,

        "honeypot_rejections": 0,
        "role_rejections": 0,
        "low_score_rejections": 0
    }

    for features in candidate_features:

        scored = calculate_final_score(
            features
        )

        rejection_reason = None

        if (
            scored["honeypot_penalty"]
            >= MAX_HONEYPOT_PENALTY
        ):

            rejection_reason = (
                "Potential honeypot profile"
            )

            summary[
                "honeypot_rejections"
            ] += 1

        elif (
            scored["role_score"]
            <= MIN_ROLE_SCORE
        ):

            rejection_reason = (
                "Poor role alignment"
            )

            summary[
                "role_rejections"
            ] += 1

        elif (
            scored["final_score"]
            < MIN_FINAL_SCORE
        ):

            rejection_reason = (
                "Low overall fit score"
            )

            summary[
                "low_score_rejections"
            ] += 1

        if rejection_reason:

            scored[
                "rejection_reason"
            ] = rejection_reason

            rejected_candidates.append(
                scored
            )

        else:

            scored_candidates.append(
                scored
            )

    scored_candidates.sort(
        key=lambda x: (
            x["final_score"],
            x["technical_score"],
            x["behavioral_score"]
        ),
        reverse=True
    )

    summary[
        "selected_candidates"
    ] = len(scored_candidates)

    summary[
        "rejected_candidates"
    ] = len(rejected_candidates)

    with open(
        "scored_candidates.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            scored_candidates,
            f,
            indent=2
        )

    with open(
        "rejected_candidates.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            rejected_candidates,
            f,
            indent=2
        )

    with open(
        "scoring_summary.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=2
        )

    print("\nScoring completed.")
    print(
        "Selected:",
        len(scored_candidates)
    )
    print(
        "Rejected:",
        len(rejected_candidates)
    )

    print("\nTop 10 Candidates:\n")

    for candidate in scored_candidates[:10]:

        print("=" * 60)

        print(
            "ID:",
            candidate["candidate_id"]
        )

        print(
            "Final:",
            candidate["final_score"]
        )

    print("\nFiles Generated:")
    print("- scored_candidates.json")
    print("- rejected_candidates.json")
    print("- scoring_summary.json")