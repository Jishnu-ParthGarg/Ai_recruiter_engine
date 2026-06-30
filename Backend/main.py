from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from recruiter_engine import get_top_candidates
from models import RankResponse


app = FastAPI(title="AI Recruiter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/rank_candidates", response_model=RankResponse)
def rank_candidates(request):

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
        raise HTTPException(status_code=500, detail=str(e))