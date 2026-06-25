import json

with open("scored_candidates.json","r") as f:
    data = json.load(f)

print(data[0])