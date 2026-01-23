# MCP Ticketing System Client

A FastAPI-based ticketing system client that leverages the Model Context Protocol (MCP), LangChain, and LangGraph to provide intelligent ticket management through AI agents.

## Overview

This project implements an AI-powered ticketing system that uses:
- **MCP (Model Context Protocol)** for server-side tool integration
- **LangChain** for LLM orchestration and tool calling
- **LangGraph** for agent state management and workflows
- **FastAPI** for REST API endpoints with streaming support
- **Langfuse** for observability and monitoring

The system supports both single-agent and multi-agent (supervisor) architectures, with capabilities for creating, reading, updating, and deleting tickets through natural language interactions.

> **Related Repository**: For the MCP server-side implementation, see [mcp-server](https://github.com/project-anak-muda/mcp-server)

## Architecture

### Agent Types

#### Single Agent
A unified agent that handles all ticket operations directly using available MCP tools.

**Capabilities:**
- Direct access to all ticketing tools
- Memory persistence via checkpointer
- Streaming responses
- Tool approval workflow with interrupts

#### Multi-Agent (Supervisor)
A supervisor agent that routes requests to specialized sub-agents:
- **Ask Agent**: Retrieves and queries ticket information
- **Create Agent**: Creates new tickets
- **Modify Agent**: Updates and deletes existing tickets

### Key Features

✅ **Natural Language Interface**: Interact with the ticketing system using plain English  
✅ **Streaming Responses**: Real-time streaming of agent responses via Server-Sent Events (SSE)  
✅ **Tool Approval Workflow**: Optional human-in-the-loop for sensitive operations  
✅ **Session Management**: Thread-based conversation persistence  
✅ **Observability**: Full tracing with Langfuse integration  
✅ **Middleware Support**: Custom interceptors for tool calls (logging, validation, approval)  

## Project Structure

```
mcp-client/
├── main_client.py              # FastAPI application entry point
├── constants/
│   ├── config.py               # Configuration and environment variables
│   ├── log.py                  # Logging setup
│   ├── mcp_setup.py            # MCP client initialization
│   ├── params.py               # Request/response models
│   └── prompt.py               # System prompts for agents
├── models/
│   └── llm.py                  # LLM model configuration
├── routers/
│   ├── single_agent.py         # Single agent endpoints
│   └── multi_agent.py          # Multi-agent supervisor endpoints
├── services/
│   ├── agent_manager.py        # Agent creation and management
│   ├── middlewares/            # Tool call interceptors
│   ├── subagents/              # Specialized sub-agents
│   └── skills/                 # Domain knowledge (*.md files)
└── utils/
    └── helpers.py              # Utility functions
```

## Installation

### Prerequisites
- Python 3.9+ (I'm using Python 3.13)
- PostgreSQL database (for ticket storage)
- MCP server running (e.g., ticketing MCP server)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-client
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# MCP Server Configuration
export MCP_SERVER_URL="http://localhost:3000/sse"

# Tool assignments for multi-agent setup
export MCP_TOOLS__ASK="get_ticket_by_id,list_tickets,search_tickets"
export MCP_TOOLS__CREATE="create_ticket,validate_ticket"
export MCP_TOOLS__MODIFY="update_ticket,delete_ticket,update_ticket_status"

# Langfuse (optional, for observability)
export LANGFUSE_PUBLIC_KEY="your-key"
export LANGFUSE_SECRET_KEY="your-secret"
export LANGFUSE_HOST="https://cloud.langfuse.com"

# LLM Configuration
export OPENAI_API_KEY="your-openai-key"
# or
export DEEPSEEK_API_KEY="your-deepseek-key"
```

4. Run the application:
```bash
python main_client.py
```

The API will be available at `http://localhost:2707`

## API Endpoints

### Single Agent Endpoints

#### Generate Answer (Non-Streaming)
```bash
POST /single-agent/generate-answer
Content-Type: application/json

{
  "query": "Show me ticket #123",
  "session_id": "user-session-001"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "final_answer": "Ticket #123: Fix login bug - Priority: high, Status: open..."
  }
}
```

**Response (Requires Approval):**
```json
{
  "status": "interrupted",
  "data": {
    "final_answer": "I'm about to delete ticket #123...",
    "message": "About to execute: delete_ticket",
    "tool_name": "delete_ticket",
    "tool_args": {"ticket_id": 123},
    "requires_approval": true,
    "session_id": "user-session-001"
  }
}
```

#### Continue Answer (After Approval)
```bash
POST /single-agent/continue-answer
Content-Type: application/json

{
  "query": "approve",  # or "reject"
  "session_id": "user-session-001"
}
```

#### Generate Answer (Streaming)
```bash
POST /single-agent/stream/generate-answer
Content-Type: application/json

{
  "query": "Create a ticket for printer issue",
  "session_id": "user-session-001"
}
```

**Response (SSE Stream):**
```
data: {"type": "agent", "content": "I'll create"}
data: {"type": "agent", "content": " a ticket"}
data: {"type": "tool", "content": "create_ticket called"}
data: {"type": "interrupt", "content": "interrupt received"}
```

#### Continue Answer (Streaming)
```bash
POST /single-agent/stream/continue-answer
```

### Multi-Agent Endpoints

Similar structure as single-agent endpoints but prefixed with `/multi-agent/`.

### Health Check
```bash
GET /health
```

## Usage Examples

### Creating a Ticket
```python
import httpx

response = httpx.post(
    "http://localhost:2707/single-agent/generate-answer",
    json={
        "query": "Create a high priority ticket for server outage in production",
        "session_id": "admin-001"
    }
)
print(response.json())
```

### Querying Tickets
```python
response = httpx.post(
    "http://localhost:2707/single-agent/generate-answer",
    json={
        "query": "Show me all open high priority tickets",
        "session_id": "support-001"
    }
)
print(response.json())
```

### Updating a Ticket
```python
response = httpx.post(
    "http://localhost:2707/single-agent/generate-answer",
    json={
        "query": "Mark ticket #456 as resolved",
        "session_id": "support-001"
    }
)
print(response.json())
```

### Streaming Example
```python
import httpx

with httpx.stream(
    "POST",
    "http://localhost:2707/single-agent/stream/generate-answer",
    json={
        "query": "List all tickets assigned to me",
        "session_id": "user-001"
    }
) as response:
    for line in response.iter_lines():
        if line.startswith("data: "):
            print(line[6:])  # Strip "data: " prefix
```

## Configuration

### MCP Server Configuration
Configure MCP servers in `constants/config.py`:
```python
MCP_SERVER_LIST = {
    "ticketing": {
        "transport": "sse",
        "url": os.getenv("MCP_SERVER_URL"),
    }
}
```

### Tool Middleware
Define tools requiring approval in `constants/config.py`:
```python
MIDDLEWARE_LIST_TOOLS = {
    "create_ticket": "Create a new ticket in the ticketing system",
    "update_ticket": "Update an existing ticket",
    "delete_ticket": "Delete a ticket (requires approval)"
}
```

### Skills (Domain Knowledge)
Add domain-specific knowledge in `services/skills/*.md` files. These are automatically loaded and injected into agent context.

## Development

### Running in Development Mode
```bash
uvicorn main_client:app --reload --port 2707 --log-config log.ini
```

### Adding New Agents
1. Create agent in `services/subagents/`
2. Add system prompt in `constants/prompt.py`
3. Register agent in `constants/mcp_setup.py`
4. Add routing logic in supervisor

### Adding Middleware
1. Create middleware in `services/middlewares/`
2. Register in `services/middlewares/compile.py`
3. Configure tool names in `constants/config.py`

## Troubleshooting

### Streaming Issues
If you encounter streaming errors with message unpacking:
```python
# Correct implementation (fixed):
async for chunk in agent.astream(..., stream_mode="messages"):
    if hasattr(chunk, 'content'):
        # Process chunk.content
```

### Session Persistence
Sessions are stored in-memory. For production, configure a persistent checkpointer:
```python
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver(connection_string)
```

### Tool Call Failures
Check Langfuse traces for detailed tool execution logs. Enable debug logging:
```python
LOGGER.setLevel(logging.DEBUG)
```

## Dependencies

Key packages:
- `fastapi==0.128.0` - Web framework
- `langgraph==1.0.6` - Agent workflows
- `langchain==1.2.4` - LLM orchestration
- `langchain-mcp-adapters==0.2.1` - MCP integration
- `langfuse==3.12.0` - Observability
- `uvicorn==0.40.0` - ASGI server

See `requirements.txt` for full list.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check Langfuse traces for debugging
- Review agent logs in `logs/` directory

## Roadmap

- [ ] PostgreSQL checkpointer for production
- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Advanced ticket search with filters
- [ ] Email notifications
- [ ] Ticket attachments support
- [ ] Analytics dashboard
- [ ] Multi-tenant support
