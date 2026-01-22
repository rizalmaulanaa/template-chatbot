from langchain.tools import tool
from langgraph.graph.state import CompiledStateGraph

from constants.mcp_setup import all_agents
from constants.prompt import CREATE_AGENT_PROMPT


@tool(
    "create_agents",
    description="""
Create new tickets in the ticketing system database.

Use this tool when you need to:
- Create a new support ticket
- Insert ticket data into the database
- Register new issues or requests
- Submit bug reports or feature requests

Input should include ticket details such as:
- Title/Subject (required)
- Description (required)
- Priority (low/medium/high/critical)
- Category or type
- Assignee (optional)
- Any other relevant metadata

Examples:
- "Create a ticket titled 'Login issue' with description 'Users cannot login' and high priority"
- "Submit a bug report for payment processing failure"
- "Create a feature request for dark mode support"
"""
)
async def create_agents(query: str) -> str:
    """
    Create a new ticket in the ticketing system.
    
    Args:
        query: A natural language description of the ticket to create, including all necessary details
        
    Returns:
        Confirmation message with the created ticket ID and details
    """
    agent: CompiledStateGraph = all_agents.get('CREATE')
    prompt = CREATE_AGENT_PROMPT.invoke(
        {"query": query}
    )
    
    result = await agent.ainvoke(prompt)
    return result["messages"][-1].content
