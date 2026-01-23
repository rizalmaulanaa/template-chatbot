from typing import List
from langchain.tools import BaseTool
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver

from models.llm import get_model
from services.subagents.ask_agent import ask_agents
from services.middlewares.compile import get_middlewares
from services.subagents.create_agent import create_agents
from services.subagents.update_agent import modify_agents
from constants.prompt import SUPERVISOR_SYSTEM_TEMPLATE, SINGLE_AGENT_SYSTEM_TEMPLATE


async def make_graph_supervisor() -> CompiledStateGraph:
    """
    Create the supervisor agent that routes requests to appropriate sub-agents.
    """
    model = get_model()
    checkpointer = InMemorySaver()
    
    supervisor = create_agent(
        model,
        tools=[ask_agents, create_agents, modify_agents],
        name="supervisor",
        system_prompt=SUPERVISOR_SYSTEM_TEMPLATE,
        checkpointer=checkpointer
    )
    
    return supervisor

async def make_graph_single(tools: List[BaseTool]) -> CompiledStateGraph:
    """
    Create the single agent that handles all requests.
    """
    model = get_model()
    checkpointer = InMemorySaver()
    middlewares = get_middlewares([tool.name for tool in tools])

    single_agent = create_agent(
        model,
        tools=tools,
        system_prompt=SINGLE_AGENT_SYSTEM_TEMPLATE,
        checkpointer=checkpointer,
        middleware=middlewares
    )

    return single_agent