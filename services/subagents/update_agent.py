from langchain.tools import tool

from constants.mcp_setup import all_agents
from constants.prompt import MODIFY_AGENT_PROMPT


@tool(
    "modify_agents",
    description="""
Update or delete existing tickets in the ticketing system database.

Use this tool when you need to:

UPDATE Operations:
- Modify ticket information (title, description, priority, status, etc.)
- Update ticket status (open, in_progress, resolved, closed)
- Change ticket priority or category
- Reassign tickets to different users
- Add notes or comments to tickets

DELETE Operations:
- Remove tickets from the system
- Delete duplicate tickets
- Clean up test or spam tickets
- Permanently remove tickets (use with caution!)

Input should include:
- Action type: "update" or "delete"
- Ticket ID (required)
- For updates: Fields to update with new values
- For deletes: Optional reason for deletion

Examples:
UPDATE:
- "Update ticket #123 status to 'resolved'"
- "Change priority of ticket 456 to 'high'"
- "Reassign ticket #789 to user John"
- "Update ticket #111 description to add more details"
- "Mark ticket #222 as closed"

DELETE:
- "Delete ticket #123"
- "Remove duplicate ticket #456"
- "Delete test ticket #789"

⚠️ WARNING: Deletion is typically permanent. Consider updating status to 'closed' instead.
"""
)
async def modify_agents(query: str) -> str:
    """
    Update or delete a ticket in the ticketing system.
    
    Args:
        query: A natural language description of what to modify (update or delete)
        
    Returns:
        Confirmation message with the operation result
    """
    agent = all_agents.get('MODIFY')
    prompt = MODIFY_AGENT_PROMPT.invoke(
        {"query": query}
    )
    
    result = await agent.ainvoke(prompt)
    return result["messages"][-1].content