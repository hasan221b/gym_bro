"""
GymExpert agent runner.

run_expert(user_id, goals) — generates a personalised training routine
for the user and returns the structured result.

Because the agent uses output_schema + output_key, the final answer is
written into session.state["exercise"] rather than a text event.
We read it from there after the run completes.
"""

import json
import logging
import uuid
from datetime import date

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.services.agentic.create_agent.gym_expert import gym_expert_agent

log = logging.getLogger(__name__)

_session_service = InMemorySessionService()
_APP_NAME = "gymbro_expert"

_runner = Runner(
    agent=gym_expert_agent,
    app_name=_APP_NAME,
    session_service=_session_service,
)


async def run_expert(user_id: int, goals: dict | None = None) -> dict:
    # Fresh session every call — avoids stale state from previous runs
    session_id = f"expert_{user_id}_{uuid.uuid4().hex}"

    await _session_service.create_session(
        app_name=_APP_NAME,
        user_id=str(user_id),
        session_id=session_id,
    )

    goals_block = (
        json.dumps(goals, indent=2, ensure_ascii=False)
        if goals
        else "Not specified — use training history to decide."
    )

    prompt = (
        f"User ID: {user_id}\n"
        f"Date: {date.today()}\n\n"
        f"User goals:\n{goals_block}\n\n"
        "Design a personalised training split for me."
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    log.info("run_expert starting for user_id=%s session=%s", user_id, session_id)

    text_fallback = None

    async for event in _runner.run_async(
        user_id=str(user_id),
        session_id=session_id,
        new_message=content,
    ):
        log.info(
            "expert event: author=%s is_final=%s",
            event.author,
            event.is_final_response(),
        )

        if hasattr(event, "error_code") and event.error_code:
            log.error(
                "expert agent error: code=%s message=%s",
                event.error_code,
                getattr(event, "error_message", ""),
            )

        if event.is_final_response() and event.content and event.content.parts:
            text_fallback = "".join(
                p.text for p in event.content.parts if hasattr(p, "text") and p.text
            ).strip()
            log.info("text_fallback captured (%d chars)", len(text_fallback))

    session = await _session_service.get_session(
        app_name=_APP_NAME,
        user_id=str(user_id),
        session_id=session_id,
    )

    structured = None
    if session and session.state:
        log.info("session.state keys: %s", list(session.state.keys()))
        structured = session.state.get("routine")
        log.info("structured output: %s", json.dumps(structured, default=str)[:500] if structured else None)

    if structured:
        return {"routine": structured, "session_id": session_id}

    if text_fallback:
        log.warning("no structured output — returning text fallback")
        return {"response": text_fallback, "session_id": session_id}

    log.error("expert produced no output at all for user_id=%s", user_id)
    return {
        "response": "GymExpert could not generate a routine. Please try again.",
        "session_id": session_id,
    }
