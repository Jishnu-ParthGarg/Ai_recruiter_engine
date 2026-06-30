from pydantic import BaseModel
from typing import List


class Candidate(BaseModel):
    candidate_id: str
    current_title: str
    years_experience: float
    location: str

    skills: List[str]

    jd_score: float
    profile_score: float
    final_score: float

    matched_skills: List[str]
    missing_skills: List[str]

    explanation: str


class RankResponse(BaseModel):
    success: bool
    count: int
    top_candidates: List[Candidate]