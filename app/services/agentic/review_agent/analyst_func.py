"""
GymAnalyst agent runner.

run_analyst(user_id, days) — triggers a one-shot analysis for the given user
and returns the formatted report string.

No conversation history is kept; every call is independent.
"""

import logging
from datetime import date

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.services.agentic.review_agent.gym_analyst import gym_analyst_agent

log = logging.getLogger(__name__)

_session_service = InMemorySessionService()
_APP_NAME = "gymbro_analyst"

_runner = Runner(
    agent=gym_analyst_agent,
    app_name=_APP_NAME,
    session_service=_session_service,
)


async def run_analyst(user_id: int, days: int = 30) -> dict:
    """
    Run a one-shot training analysis for the user and return the report.

    A fresh session is created for each call so there is no state bleed
    between requests.

    Args:
        user_id: The user's database ID.
        days:    Number of days of history to analyse (default 30).

    Returns:
        Dict with keys ``report`` and ``session_id``.
    """
    session_id = f"analyst_{user_id}_{date.today().isoformat()}"

    existing = await _session_service.get_session(
        app_name=_APP_NAME,
        user_id=str(user_id),
        session_id=session_id,
    )
    if not existing:
        await _session_service.create_session(
            app_name=_APP_NAME,
            user_id=str(user_id),
            session_id=session_id,
        )

    prompt = (
        f"User ID: {user_id}\n"
        f"Date: {date.today()}\n"
        f"Analysis window: last {days} days\n\n"
        "Please run all tools and produce the full training report."
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    result = None
    async for event in _runner.run_async(
        user_id=str(user_id),
        session_id=session_id,
        new_message=content,
    ):
        log.debug("analyst event: author=%s is_final=%s", event.author, event.is_final_response())

        # Capture any error surfaced as an event
        if hasattr(event, "error_code") and event.error_code:
            log.error("analyst agent error: code=%s message=%s", event.error_code, getattr(event, "error_message", ""))

        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(
                part.text
                for part in event.content.parts
                if hasattr(part, "text") and part.text
            ).strip()

            log.debug("analyst final text length: %d", len(final_text))
            if final_text:
                result = {"report": final_text, "session_id": session_id}

    if not result:
        log.warning("analyst produced no final response for user_id=%s days=%s", user_id, days)

    return result or {
        "report": "The analyst could not generate a report. Please try again.",
        "session_id": session_id,
    }
