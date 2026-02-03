from constants.log import LOGGER
from models.llm import get_model
from constants.params import RAGState
from constants.prompt import GENERATE_PROMPT


async def generate_answer(state: RAGState):
    """Generate an answer from the retrieved docs."""
    LOGGER.info("Inside Generate Answer")
    query = state.get("query", "")
    retrieved_docs = state.get("retrieved_docs", [])
    model = get_model()

    prompt = GENERATE_PROMPT.invoke({
        "question": query,
        "context": "\n".join(retrieved_docs),
    })
    response = await model.ainvoke(prompt)

    return {"final_answer": response.content}