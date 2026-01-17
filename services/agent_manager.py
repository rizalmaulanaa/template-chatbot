from models.llm import get_model
from langchain.agents import create_agent
from services.subagents.ask_agent import ask_agents
from constants.prompt import SUPERVISOR_SYSTEM_TEMPLATE
from services.subagents.create_agent import create_agents
from services.subagents.update_agent import modify_agents
    
async def make_graph():
    """
    Create the supervisor agent that routes requests to appropriate sub-agents.
    """
    model = get_model()
    
    supervisor = create_agent(
        model,
        tools=[ask_agents, create_agents, modify_agents],
        system_prompt=SUPERVISOR_SYSTEM_TEMPLATE
    )
    
    return supervisor