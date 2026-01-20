from typing import List

from constants.log import LOGGER
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from models.llm import get_model
from utils.helpers import split_agent_tools
from constants.config import MCP_SERVER_LIST, MCP_TOOLS, MIDDLEWARE_LIST_TOOLS


all_agents = {}

async def logging_interceptor(
    request: MCPToolCallRequest,
    handler,
):
    """Log tool calls before and after execution."""
    LOGGER.info(f"Calling tool: {request.name} with args: {request.args}")
    result = await handler(request)
    LOGGER.info(f"Tool {request.name} returned: {result}")
    
    return result

def get_middlewares(tools_names: List[str]):
    middlewares = []
    
    # Build interrupt_on config for all tools at once
    interrupt_on = {}
    description_parts = []
    
    for tool_name in tools_names:
        if tool_name in MIDDLEWARE_LIST_TOOLS:
            desc_tool = MIDDLEWARE_LIST_TOOLS.get(tool_name)
            
            # Add this tool to the interrupt config
            interrupt_on[tool_name] = True
            description_parts.append(f"{tool_name}: {desc_tool}")
    
    # Only create ONE middleware instance if we have any tools to monitor
    if interrupt_on:
        # Special case for execute_sql if needed
        if "execute_sql" in tools_names:
            interrupt_on["execute_sql"] = {"allowed_decisions": ["approve", "reject"]}
        
        # Combine descriptions
        description_prefix = "\n".join(description_parts)
        
        temp = HumanInTheLoopMiddleware(
            interrupt_on=interrupt_on,
            description_prefix=description_prefix,
        )
        
        middlewares.append(temp)
            
    return middlewares

async def setup_agent():
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