# generate_submission.py

import json
import csv

with open("top_candidates.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)

candidates = sorted(
    candidates,
    key=lambda c: (
        -c["final_score"],
        c["candidate_id"]
    )
)

with open(
    "submission.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "candidate_id",
        "rank",
        "score",
        "reasoning"
    ])

    for rank, candidate in enumerate(
        candidates[:100],
        start=1
    ):

        reasoning = candidate.get(
            "explanation",
            ""
        ).replace("\n", " ").strip()

        writer.writerow([
            candidate["candidate_id"],
            rank,
            f"{candidate['final_score']:.2f}",
            reasoning
        ])

print("submission.csv generated.")