import logging

from fastapi import APIRouter, HTTPException

from app.schemas.agent import CreateRoutineRequest, CreateRoutineResponse
from app.services.agentic.create_agent.expert_func import run_expert

log = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/create-routine", response_model=CreateRoutineResponse)
async def create_routine(req: CreateRoutineRequest):
    try:
        log.info("create-routine called: user_id=%s", req.user_id)
        result = await run_expert(
            user_id=req.user_id,
            goals=req.answers.model_dump(),
        )
        routine = result.get("routine")
        response = result.get("response")
        log.info(
            "create-routine result: routine=%s, response=%s",
            "present" if routine else "None",
            "present" if response else "None",
        )
        if routine:
            log.info("routine keys: %s", list(routine.keys()) if isinstance(routine, dict) else type(routine))
        return CreateRoutineResponse(routine=routine, response=response)
    except Exception as e:
        log.exception("create-routine failed")
        raise HTTPException(status_code=500, detail=str(e))
