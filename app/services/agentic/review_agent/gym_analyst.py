from google.adk.agents import Agent

from app.services.agentic.review_agent.analyst_tools import (
    get_user_session_logs,
    get_volume_by_muscle,
    get_exercise_prs,
    get_routine_exercises,
    get_body_metrics,
    get_avg_session_duration,
)

from app.services.agentic.review_agent.prompt import _INSTRUCTION

gym_analyst_agent = Agent(
    name="gym_analyst_agent",
    model="gemini-3-flash-preview",
    description=(
        "Fetches and analyses the user's training data — session logs, volume, "
        "PRs, and routine structure. Call this for any progress summary or routine rating."
    ),
    instruction=_INSTRUCTION,
    tools=[
        get_user_session_logs,
        get_volume_by_muscle,
        get_exercise_prs,
        get_routine_exercises,
        get_body_metrics,
        get_avg_session_duration,
    ],
)
