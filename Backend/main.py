from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recruiter_engine import get_top_candidates

app = FastAPI(title="AI Recruiter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change to your frontend URL after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RankRequest(BaseModel):
    job_description: str
    top_k: int = 5


@app.get("/")
def home():
    return {
        "message": "AI Recruiter Backend Running 🚀"
    }


@app.post("/rank_candidates")
def rank_candidates(request: RankRequest):
    try:
        candidates = get_top_candidates(
            request.job_description,
            request.top_k
        )

        return {
            "success": True,
            "count": len(candidates),
            "top_candidates": candidates
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }