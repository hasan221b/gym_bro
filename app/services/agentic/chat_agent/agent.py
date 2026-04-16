from google.adk.agents import Agent
from google.adk.tools import AgentTool, google_search
from app.services.agentic.chat_agent.tools import get_data
from app.services.agentic.chat_agent.prompt import build_instructions

_search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash-lite",
    description="Searches the web for fitness information: exercise science, training methods, muscle anatomy, and evidence-based programming.",
    instruction=(
        "You are a fitness research specialist. "
        "Use google_search to find accurate, evidence-based information about training, exercise science, and nutrition. "
        "Prefer trusted sources: site:pubmed.ncbi.nlm.nih.gov OR site:strongerbyscience.com OR site:examine.com OR site:menshealth.com. "
        "Return a 2-3 sentence summary of the most relevant finding only. No lists, no URLs, no extra detail."
    ),
    tools=[google_search],
)

root_agent = Agent(
    name="Rex",
    model="gemini-2.5-flash",
    description="Rex — AI fitness coach for GymBro. Analyses workout data, rates routines, and gives evidence-based training advice.",
    instruction=build_instructions(),
    tools=[get_data, AgentTool(agent=_search_agent)],
)
