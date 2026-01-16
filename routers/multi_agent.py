import uuid

from typing import Dict
from langchain.messages import HumanMessage, AIMessage, ToolMessage
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from fastapi import APIRouter, HTTPException, Request, Depends

from utils.helpers import parse_response
from constants.params import ChatbotParams


multi_agent_router = APIRouter(
    tags=["MULTI AGENT ENDPOINT"],
    responses={404: {"description": "Not found"}},
    prefix="/multi-agent"
)

def get_manager(request: Request):
    """Dependency to get manager from app context"""
    if not hasattr(request.app, 'context') or 'agents' not in request.app.context:
        raise HTTPException(
            status_code=503,
            detail="Service Manager not available"
        )
    return request.app.context['agents']

@multi_agent_router.post("/generate-answer")
async def generate_answer(
    payload: ChatbotParams,
    agents: Dict = Depends(get_manager)
):
    run_id = str(uuid.uuid4())
    
    try:
        # current_state = {
        #     "query": payload.query,
        #     "messages": HumanMessage(payload.query)
        # }
        # config = {
        #     "configurable": {
        #         "thread_id": payload.session_id,
        #         "index_": payload.index_,
        #         "limit_docs": payload.limit_docs
        #     },
        #     "run_name" : f"{payload.session_id}_{run_id}",
        #     "run_id" : run_id,
        # }
        
        chatbot_graph = agents['main_agent']
        response = await chatbot_graph.ainvoke(
            {"messages": [{"role": "user", "content": payload.query}]}
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