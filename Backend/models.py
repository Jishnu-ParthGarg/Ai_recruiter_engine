from pydantic import BaseModel
from typing import List


class CandidateRequest(BaseModel):
    job_description: str
    top_k: int = 10


class CandidateResponse(BaseModel):
    candidate_id: str
    final_score: float
    explanation: str