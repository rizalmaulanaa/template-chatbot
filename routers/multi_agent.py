import uuid

from fastapi import APIRouter
from langchain_core.messages import HumanMessage


multi_agent_router = APIRouter(
    tags=["MULTI AGENT ENDPOINT"],
    responses={404: {"description": "Not found"}},
    prefix="/multi-agent"
)


@multi_agent_router.post("/generate-answer")
async def generate_answer(payload):
    pass
    # run_id = str(uuid.uuid4())
    
    # try:
    #     current_state = {
    #         "query": payload.query,
    #         "messages": HumanMessage(payload.query)
    #     }
    #     config = {
    #         "configurable": {
    #             "thread_id": payload.session_id,
    #             "index_": payload.index_,
    #             "limit_docs": payload.limit_docs
    #         },
    #         "run_name" : f"{payload.session_id}_{run_id}",
    #         "run_id" : run_id,
    #     }
        
    #     chatbot_graph = await make_graph()
    #     response = await chatbot_graph.ainvoke(current_state, config)
        
    #     response = parse_response(response)
    #     return {
    #         "status": "success",
    #         "data": response
    #     }
    # except Exception as e:
    #     return {
    #         "status": "error",
    #         "data": {"final_answer" : f"Found error with {e}"}
    #     }