"""
Rex agent runner.

run_rex(user_id, message, session_id) — sends a message to Rex and returns his reply.

One session per user is kept alive in memory so Rex remembers the conversation
history across multiple messages in the same chat.
"""

from datetime import date

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.services.agentic.chat_agent.agent import root_agent

# ── Session store (lives for the lifetime of the process) ─────────────────────
_session_service = InMemorySessionService()
_APP_NAME = "gymbro"

# ── Runner (one shared instance) ──────────────────────────────────────────────
_runner = Runner(
    agent=root_agent,
    app_name=_APP_NAME,
    session_service=_session_service,
)


async def run_rex(user_id: int, message: str) -> str:
    """
    Send a message to Rex and return his text reply.

    A session is created on the first message for each user and reused on
    subsequent messages — Rex remembers the full conversation history.

    Args:
        user_id: Telegram user ID (used as both user identifier and session key).
        message: The user's raw message text.

    Returns:
        Rex's response as a plain string.
    """
    session_id = str(user_id)

    existing = await _session_service.get_session(
        app_name=_APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )
    if not existing:
        await _session_service.create_session(
            app_name=_APP_NAME,
            user_id=session_id,
            session_id=session_id,
        )

    full_message = (
        f"User ID: {user_id}\n"
        f"Date: {date.today()}\n\n"
        f"{message}"
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=full_message)],
    )

    result = None
    async for event in _runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = "".join(
                part.text
                for part in event.content.parts
                if hasattr(part, "text") and part.text
            ).strip()

            if final_response:
                result = {
                    "response": final_response,
                    "session_id": session_id,
                }

    return result or {"response": "I couldn't generate a response. Please try again.", "session_id": session_id}
