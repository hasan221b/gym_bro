from fastapi import APIRouter, HTTPException

from app.schemas.agent import ReviewRequest, ReviewResponse
from app.services.agentic.review_agent.analyst_func import run_analyst

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/review", response_model=ReviewResponse)
async def review(req: ReviewRequest):
    try:
        result = await run_analyst(req.user_id, req.days)
        report = result.get("report") if isinstance(result, dict) else result
        return ReviewResponse(report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
