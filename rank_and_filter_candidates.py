import json
from typing import List, Dict


# ==========================================
# BUSINESS RULES (SOFT FILTERING - SAFE)
# ==========================================

def apply_business_rules(candidates: List[Dict]) -> List[Dict]:

    filtered = []

    print("Applying business rules...")

    for candidate in candidates:

        try:
            years = candidate.get("years_of_experience", 0)
            role_score = candidate.get("role_score", 0)
            honeypot = candidate.get("honeypot_penalty", 0)
            final_score = candidate.get("final_score", 0)

            # ----------------------------------
            # SOFT PENALTIES (NOT HARD REJECTS)
            # ----------------------------------

            penalty = 0

            # Honeypot penalty
            if honeypot >= 25:
                penalty += 30

            # Poor role fit
            if role_score <= -50:
                penalty += 20

            # Low experience penalty (NOT REMOVE)
            if years < 2:
                penalty += 10

            # Very weak score penalty
            if final_score < 25:
                penalty += 10

            candidate["final_score"] = final_score - penalty

            filtered.append(candidate)

        except Exception as e:
            print(f"Skipping candidate due to error: {e}")
            continue

    return filtered


# ==========================================
# RANKING LOGIC
# ==========================================

def rank_candidates(candidates: List[Dict]) -> List[Dict]:

    return sorted(
        candidates,
        key=lambda c: (
            -c.get("final_score", 0),
            c.get("candidate_id", "")
        )
    )


# ==========================================
# EXPLAINABILITY
# ==========================================

def explain_candidate(candidate):

    reasons = []

    if candidate.get("technical_score", 0) >= 35:
        reasons.append("strong technical fit")

    if candidate.get("behavioral_score", 0) >= 15:
        reasons.append("high recruiter engagement")

    if candidate.get("role_score", 0) >= 10:
        reasons.append("good alignment with the target role")

    if candidate.get("logistics_score", 0) >= 5:
        reasons.append("favorable notice period")

    if not reasons:
        reasons.append("balanced profile")

    return (
        f"Candidate demonstrates {', '.join(reasons)}. "
        f"Ranking is based on overall skills, experience, and role fit."
    )


# ==========================================
# TOP PIPELINE
# ==========================================

def get_top_candidates(candidates: List[Dict], top_k: int = 100):

    print("Applying business rules...")

    filtered = apply_business_rules(candidates)

    print(f"Candidates after filtering: {len(filtered)}")

    print("Ranking candidates...")

    ranked = rank_candidates(filtered)

    top_candidates = ranked[:top_k]

    print("Generating explanations...")

    for candidate in top_candidates:
        candidate["explanation"] = explain_candidate(candidate)

    print(f"Top candidates selected: {len(top_candidates)}")

    return top_candidates


# ==========================================
# SAVE RESULTS
# ==========================================

def save_results(candidates: List[Dict], filename: str = "top_candidates.json"):

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2)

        print(f"Saved results to {filename}")

    except Exception as e:
        print(f"Error saving file: {e}")


# ==========================================
# MAIN (SAFE TEST MODE)
# ==========================================

if __name__ == "__main__":

    print("Loading scored candidates...")

    with open("scored_candidates.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)

    print(f"Total candidates: {len(candidates)}")

    top_candidates = get_top_candidates(candidates, top_k=100)

    print("\nTop 10 Candidates:\n")

    for candidate in top_candidates[:10]:
        print("=" * 60)
        print("Candidate ID:", candidate.get("candidate_id"))
        print("Final Score:", candidate.get("final_score"))
        print(candidate.get("explanation"))

    save_results(top_candidates)

    print("\nPipeline completed successfully.")