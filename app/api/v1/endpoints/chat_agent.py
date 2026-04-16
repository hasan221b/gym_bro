from fastapi import APIRouter, HTTPException
from app.schemas.agent import ChatRequest, AgentResponse
from app.services.agentic.chat_agent.agent_func import run_rex

router = APIRouter(prefix="/agent", tags=["Agent"])





@router.post("/chat", response_model=AgentResponse)
async def chat(req: ChatRequest):
    try:
        result = await run_rex(req.user_id, req.message)
        reply = result.get("response") if isinstance(result, dict) else result
        return AgentResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
