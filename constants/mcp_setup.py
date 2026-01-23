from typing import List, Union, Dict
from langchain.tools import BaseTool
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from constants.log import LOGGER
from models.llm import get_model
from utils.helpers import split_agent_tools
from constants.config import MCP_SERVER_LIST, MCP_TOOLS
from services.middlewares.compile import get_middlewares


all_agents = {}

async def logging_interceptor(
    request: MCPToolCallRequest,
    handler,
):
    """Log tool calls before and after execution."""
    LOGGER.info(f"Calling tool: {request.name} with args: {request.args}")
    result = await handler(request)
    LOGGER.info(f"Tool {request.name}")
    
    return result

async def setup_agent() -> Union[Dict[str, CompiledStateGraph], List[BaseTool]]:
    global all_agents
    
    client = MultiServerMCPClient(
        MCP_SERVER_LIST,
        tool_interceptors=[logging_interceptor],
    )
    
    tools = await client.get_tools()
    model = get_model()
    
    for agent_name, list_tool_available in MCP_TOOLS.items():
        used_tools = split_agent_tools(tools, list_tool_available)
        middlewares = get_middlewares(list_tool_available)
        
        agent = create_agent(
            model, 
            tools=used_tools,
            name=f"{agent_name.lower()}_agent",
            system_prompt=f"You are a {agent_name.lower()} agent.",
            middleware=middlewares
        )
        
        all_agents[agent_name] = agent
    
    return all_agents, tools