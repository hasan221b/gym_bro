from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: int
    message: str


class AgentResponse(BaseModel):
    reply: str


class ReviewRequest(BaseModel):
    user_id: int
    days: int = Field(default=30, ge=1, le=365, description="How many days back to analyse")


class ReviewResponse(BaseModel):
    report: str


class OnboardingAnswers(BaseModel):
    primary_goal: str = Field(
        description="Primary goal and deadline, e.g. 'build muscle, 3-month deadline'."
    )
    age: str = Field(
        description="User's age in years, e.g. '25'."
    )
    height_cm: str = Field(
        description="User's height in cm, e.g. '178'."
    )
    weight_kg: str = Field(
        description="User's current body weight in kg, e.g. '82'."
    )
    training_availability: str = Field(
        description="Days per week and session duration, e.g. '4 days, 60 min each'."
    )
    recovery_and_sleep: str = Field(
        description="Recovery score 1–10 and average sleep hours, e.g. '7/10, 7.5 hrs'."
    )
    injuries: str = Field(
        default="None",
        description="Past injuries or movement restrictions, or 'None'."
    )
    training_background: str = Field(
        description="Training done in the last 6 months, e.g. 'bodybuilding, 3x/week'."
    )
    training_preference: str = Field(
        description="Performance, appearance, or fun/enjoyment."
    )


class CreateRoutineRequest(BaseModel):
    user_id: int
    answers: OnboardingAnswers


class CreateRoutineResponse(BaseModel):
    routine: dict | None = None
    response: str | None = None