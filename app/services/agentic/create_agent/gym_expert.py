from google.adk.agents import Agent
from app.services.agentic.create_agent.prompt import build_instructions

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

class ExerciseContent(BaseModel):
    name: str = Field(
        description="The exercise name, e.g. 'Barbell Squat'"
    )
    force: str = Field(
        description="Force type: 'push', 'pull', or 'static'"
    )
    level: str = Field(
        description="Difficulty level: 'beginner', 'intermediate', or 'expert'"
    )
    primary_muscles: list[str] = Field(
        description="Primary muscles targeted by the exercise."
    )
    secondary_muscles: list[str] = Field(
        description="Secondary muscles targeted by the exercise."
    )
    equipment: str = Field(
        description="Equipment needed, e.g. 'barbell', 'dumbbell', 'body_only'"
    )
    planned_sets: int = Field(
        description="Number of sets to perform."
    )
    planned_reps: int = Field(
        description="Target reps per set."
    )
    planned_weight: float | None = Field(
        description="Target weight in kg, or null for bodyweight exercises."
    )


class DayPlan(BaseModel):
    day: int = Field(description="Day number, e.g. 1, 2, 3")
    focus: str = Field(description="Training focus for this day, e.g. 'Push', 'Pull', 'Legs', 'Upper Body', 'Full Body'")
    exercises: list[ExerciseContent] = Field(description="Exercises for this training day.")


class RoutineOutput(BaseModel):
    days: list[DayPlan] = Field(description="One entry per training day.")


gym_expert_agent = Agent(

    name="gym_expert_agent",
    model = "gemini-3-flash-preview",
    description="Gym Expert — an AI agent specializing in gym workouts, exercise science, and training methods. Provides evidence-based advice on programming, technique, and recovery.",
    instruction = build_instructions(),
    output_schema=RoutineOutput,
    output_key="routine",
)
