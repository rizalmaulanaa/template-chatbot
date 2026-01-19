import uuid

from typing import List
from langgraph.types import Command
from langchain.messages import AIMessage
from langgraph.graph.state import CompiledStateGraph
from fastapi import APIRouter, HTTPException, Request, Depends

from constants.log import LOGGER
from constants.params import ChatbotParams
from constants.config import LANGFUSE_HANDLER


single_agent_router = APIRouter(
    tags=["SINGLE AGENT ENDPOINT"],
    responses={404: {"description": "Not found"}},
    prefix="/single-agent"
)

def get_single_agent(request: Request):
    """Dependency to get tools from app context"""
    if not hasattr(request.app, 'context') or 'single_agent' not in request.app.context:
        raise HTTPException(
            status_code=503,
            detail="Tools not available"
        )
    return request.app.context['single_agent']

@single_agent_router.post("/generate-answer")
async def generate_answer(
    payload: ChatbotParams,
    single_agent: CompiledStateGraph = Depends(get_single_agent)
):
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name": f"{payload.session_id}_{run_id}",
            "run_id": run_id,
            "callbacks": [LANGFUSE_HANDLER],
        }

        response = await single_agent.ainvoke(
            {"messages": [{"role": "user", "content": payload.query}]},
            config=config
        )
        
        # Check if there's an interrupt
        interrupts = response.get('__interrupt__', [])
        
        # Get the final AI message
        final_ai_message = next(
            (msg for msg in reversed(response["messages"]) if isinstance(msg, AIMessage)),
            None
        )
        
        if interrupts:
            interrupt_data = interrupts[0].value
            action_requests = interrupt_data.get('action_requests', [])
            
            # Get the action details
            action = action_requests[0] if action_requests else {}
            
            return {
                "status": "interrupted",
                "data": {
                    "final_answer": final_ai_message.content,
                    "message": f"About to execute: {action.get('name')}",
                    "description": action.get('description'),
                    "tool_name": action.get('name'),
                    "tool_args": action.get('args'),
                    "session_id": payload.session_id,
                    "requires_approval": True
                }
            }
        
        if not final_ai_message:
            return {
                "status": "error",
                "data": {"final_answer": "No AI response found"}
            }
                    
        return {
            "status": "success",
            "data": final_ai_message.content
        }
    except Exception as e:
        LOGGER.error(f"Error in generate_answer: {e}", exc_info=True)
        return {
            "status": "error",
            "data": {"final_answer": f"Found error with {e}"}
        }
        
@single_agent_router.post("/continue-answer")
async def continue_answer(
    payload: ChatbotParams,
    single_agent: CompiledStateGraph = Depends(get_single_agent)
):
    run_id = str(uuid.uuid4())
    
    try:
        config = {
            "configurable": {
                "thread_id": payload.session_id,
            },
            "run_name" : f"{payload.session_id}_{run_id}",
            "run_id" : run_id,
            "callbacks" : [LANGFUSE_HANDLER],
        }

        response = await single_agent.ainvoke(
            Command( 
                resume={"decisions": [{"type": payload.query}]}
            ), 
            config=config
        )
         
        final_ai_message = next(
            msg for msg in reversed(response["messages"])
            if isinstance(msg, AIMessage)
        )
                    
        return {
            "status": "success",
            "data": final_ai_message.content
        }
    except Exception as e:
        return {
            "status": "error",
            "data": {"final_answer" : f"Found error with {e}"}
        }