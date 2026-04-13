from google.adk.agents import Agent
from app.services.agentic.tools import get_data, create_routine
from app.services.agentic.prompt import build_instructions


gym_expert_agent = Agent(

    name="gym_expert_agent",
    model = "gemini-2.5-flash",
    description="Gym Expert — an AI agent specializing in gym workouts, exercise science, and training methods. Provides evidence-based advice on programming, technique, and recovery.",
    instruction = "",
    tools = [get_data]
)