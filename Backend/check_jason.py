import json

with open("../scored_candidates.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Total candidates:", len(data))
print("\nFirst candidate:\n")
print(data[0])