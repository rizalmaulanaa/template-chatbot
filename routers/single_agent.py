import uuid

from typing import List
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from fastapi import APIRouter, HTTPException, Request, Depends

from constants.params import ChatbotParams
from services.agent_manager import make_graph_single


single_agent_router = APIRouter(
    tags=["SINGLE AGENT ENDPOINT"],
    responses={404: {"description": "Not found"}},
    prefix="/single-agent"
)

def get_tools(request: Request):
    """Dependency to get tools from app context"""
    if not hasattr(request.app, 'context') or 'tools' not in request.app.context:
        raise HTTPException(
            status_code=503,
            detail="Tools not available"
        )
    return request.app.context['tools']

@single_agent_router.post("/generate-answer")
async def generate_answer(
    payload: ChatbotParams,
    tools: List = Depends(get_tools)
):
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name" : f"{payload.session_id}_{run_id}",
            "run_id" : run_id,
        }

        chatbot_graph = await make_graph_single(tools)
        response = await chatbot_graph.ainvoke(
            {"messages": [{"role": "user", "content": payload.query}]},
            config=config
        )
        
        final_ai_message = next(
            msg for msg in reversed(response["messages"])
            if isinstance(msg, AIMessage)
        )
                    
        # response = parse_response(response)
        return {
            "status": "success",
            "data": final_ai_message.content
        }
    except Exception as e:
        return {
            "status": "error",
            "data": {"final_answer" : f"Found error with {e}"}
        }