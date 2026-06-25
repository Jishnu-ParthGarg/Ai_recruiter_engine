import gzip
import json

def load_candidates(filename):
    candidates = []

    try:
        with gzip.open(filename, "rt", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    candidate = json.loads(line)
                    candidates.append(candidate)

        return candidates

    except FileNotFoundError:
        print("Error: File not found.")
        return []

    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return []


# Main Program
filename = "candidates.jsonl.gz"

print("Loading candidates...")

candidates = load_candidates(filename)

print("Total candidates loaded:", len(candidates))


# Display details of the first candidate
if candidates:
    print("\nFirst Candidate Details:")

    first_candidate = candidates[0]

    print("Candidate ID:",
          first_candidate.get("candidate_id", "N/A"))

    profile = first_candidate.get("profile", {})

    print("Current Title:",
          profile.get("current_title", "N/A"))

    print("Years of Experience:",
          profile.get("years_of_experience", "N/A"))

    print("Current Company:",
          profile.get("current_company", "N/A"))

    print("Current Location:",
          profile.get("current_location", "N/A"))

    print("\nSkills:")

    skills = first_candidate.get("skills", [])
    print(type(skills))
    print(skills[:2])
    for skill in skills[:10]:
        name = skill.get("name", "N/A")
        proficiency = skill.get("proficiency", "N/A")
        duration = skill.get("duration_months", "N/A")
        print(f"- {name} ({proficiency}), {duration} months")

    print("\nCareer History:")

    career = first_candidate.get("career_history", [])

    for job in career:
        print(
            f"- {job['title']} at {job['company']} "
            f"({job['duration_months']} months)"
        )

    print("\nRedrob Signals:")
    signals = first_candidate.get("redrob_signals", {})
    print("Open to work:",
        signals.get("open_to_work_flag"))
    print("Recruiter response rate:",
        signals.get("recruiter_response_rate"))
    print("Notice period:",
        signals.get("notice_period_days"))
    print("Willing to relocate:",
        signals.get("willing_to_relocate"))
    print("Interview completion rate:",
        signals.get("interview_completion_rate"))