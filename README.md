# FastAPI Chatbot Template

A minimal yet extensible template for building production-ready chatbots using **FastAPI**, **Uvicorn**, and **LangChain**.

Use this repository as a starting point to quickly spin up an LLM-powered chatbot API (for support bots, internal assistants, FAQ bots, etc.) and customize the behavior with LangChain chains, tools, and memory.

## Features

- 🚀 **FastAPI + Uvicorn** for high‑performance async APIs
- 🧠 **LangChain** for LLM orchestration, tools, and memory
- 💬 **Chat endpoint** ready to plug into a frontend (web / mobile / Slack / etc.)
- 🧩 Pluggable prompt templates and chains
- 🧵 Optional conversational memory per user/session
- 🔧 Simple configuration via environment variables

## Project Structure

```text
template-chatbot/
├── main.py              # FastAPI application entry point
├── chat/                # Chat logic and LangChain integration
│   ├── chains.py        # LangChain chains / pipelines
│   ├── prompts.py       # System & user prompt templates
│   └── schemas.py       # Pydantic request/response models
├── config.py            # Settings & environment variables
├── requirements.txt     # Python dependencies
└── README.md
```

> The exact structure in your repo may differ slightly, but the idea is the same: keep API, config, and LangChain logic separated.

## Getting Started

### Prerequisites

- Python 3.9+ (I'm using Python 3.13)
- An LLM provider API key (e.g. OpenAI, DeepSeek, etc.)

### Installation

1. Clone the repository

```bash
git clone <repository-url>
cd template-chatbot
```

2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

### Configuration

Set the required environment variables (adapt to the LLM you use):

```bash
# LLM configuration
export OPENAI_API_KEY="your-openai-key"           # or
export DEEPSEEK_API_KEY="your-deepseek-key"

# Optional: server config
export APP_HOST="0.0.0.0"
export APP_PORT="8000"
```

You can also centralize these in a `.env` file and load them in `config.py` using `python-dotenv` or Pydantic settings.

## Running the Server

Run the FastAPI app with Uvicorn (development mode):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` and the interactive docs at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API

### `POST /chat`

Send a message to the chatbot and get a response.

**Request body** (example):

```json
{
  "message": "Hello, who are you?",
  "session_id": "user-123"  // optional, for conversation memory
}
```

**Response** (example):

```json
{
  "status": "success",
  "data": {
    "final_answer": "hi"
  }
}
```

The actual Pydantic models live in `chat/schemas.py` and can be extended with extra fields (metadata, user id, language, etc.).

## Customization Ideas

- Add authentication (API key, JWT, OAuth)
- Connect to a vector store and build a **RAG** chatbot
- Add streaming responses using `StreamingResponse` or server‑sent events
- Instrument logging / tracing (e.g. Langfuse, OpenTelemetry)
- Package and deploy with Docker / Kubernetes / serverless

## Development

- Run formatters/linters (if configured), e.g. `ruff`, `black`, `mypy`
- Add tests around your chat chains and FastAPI routes using `pytest` and `httpx`

## License

See [LICENSE](LICENSE) file for details.

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

## License

See [LICENSE](LICENSE) file for details.