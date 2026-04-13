from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.agentic.agent_func import run_rex

router = APIRouter(prefix="/agent", tags=["Agent"])


class ChatRequest(BaseModel):
    user_id: int
    message: str


class AgentResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=AgentResponse)
async def chat(req: ChatRequest):
    try:
        reply = await run_rex(req.user_id, req.message)
        return AgentResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
