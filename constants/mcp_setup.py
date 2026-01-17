from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from models.llm import get_model
from utils.helpers import split_agent_tools
from constants.config import MCP_SERVER_LIST, MCP_TOOLS

all_agents = {}

async def setup_agent():
    global all_agents
    
    client = MultiServerMCPClient(MCP_SERVER_LIST)
    
    tools = await client.get_tools()
    model = get_model()
    
    for agent_name, list_tool_available in MCP_TOOLS.items():
        used_tools = split_agent_tools(tools, list_tool_available)
        agent = create_agent(
            model, 
            tools=used_tools,
            system_prompt=f"You are a {agent_name.lower()} agent."
        )
        
        all_agents[agent_name] = agent

    return all_agents