from langgraph.checkpoint.memory import InMemorySaver  

from models.llm import get_model
from langchain.agents import create_agent
from services.subagents.ask_agent import ask_agents
from services.subagents.create_agent import create_agents
from services.subagents.update_agent import modify_agents
from constants.prompt import SUPERVISOR_SYSTEM_TEMPLATE, SINGLE_AGENT_SYSTEM_TEMPLATE
    
    
async def make_graph_supervisor():
    """
    Create the supervisor agent that routes requests to appropriate sub-agents.
    """
    model = get_model()
    checkpointer = InMemorySaver()
    
    supervisor = create_agent(
        model,
        tools=[ask_agents, create_agents, modify_agents],
        system_prompt=SUPERVISOR_SYSTEM_TEMPLATE,
        checkpointer=checkpointer
    )
    
    return supervisor

async def make_graph_single(tools):
    """
    Create the single agent that handles all requests.
    """
    model = get_model()
    checkpointer = InMemorySaver()
    
    single_agent = create_agent(
        model,
        tools=tools,
        system_prompt=SINGLE_AGENT_SYSTEM_TEMPLATE,
        checkpointer=checkpointer
    )

    return single_agent