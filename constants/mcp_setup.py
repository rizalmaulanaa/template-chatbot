from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from models.llm import get_model

async def setup_agent():
    client = MultiServerMCPClient(
        {
            "ticketing": {
                "transport": "sse",
                "url": "http://localhost:8055/sse", 
            }
        }
    )
    tools = await client.get_tools()
    model = get_model()
    agent = create_agent(model, tools)
    
    all_agents = {
        'main_agent': agent
    }

    return all_agents