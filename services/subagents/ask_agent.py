from langchain.tools import tool
from langgraph.graph.state import CompiledStateGraph

from constants.mcp_setup import all_agents
from constants.prompt import ASK_AGENT_PROMPT


@tool(
    "ask_agents",
    description="""
Query and retrieve ticket information from the database.

Use this tool when you need to:
- Get a specific ticket by ID
- List all tickets
- Search or filter tickets
- Retrieve ticket details, status, or history

Input should be a clear query about what ticket information you need.
Examples:
- "Get ticket with ID 123"
- "List all open tickets"
- "Show me all tickets created today"
- "Find tickets assigned to user X"
"""
)
async def ask_agents(query: str) -> str:
    """
    Retrieve ticket information from the database.
    
    Args:
        query: A natural language query describing what ticket information to retrieve
        
    Returns:
        The ticket information or list of tickets
    """
    agent: CompiledStateGraph = all_agents.get('ASK')
    prompt = ASK_AGENT_PROMPT.invoke(
        {"query": query}
    )
    
    result = await agent.ainvoke(prompt)
    return result["messages"][-1].content