from typing import Literal

from constants.log import LOGGER
from models.llm import get_model
from constants.config import MAX_REWRITE_ITERATIONS
from constants.params import RAGState, GradeDocuments
from constants.prompt import REWRITE_PROMPT, GRADE_PROMPT


async def rewrite_question(state: RAGState):
    """Rewrite the original user question."""
    LOGGER.info("Inside Rewrite Question")
    query = state.get("query", "")
    iteration_count = state.get("iteration_count", 0)
    model = get_model()

    # Skip rewrite on the very first pass — use the original query as-is
    if iteration_count == 0:
        return {
            "query": query,
            "iteration_count": iteration_count + 1,
        }

    prompt = REWRITE_PROMPT.invoke({"question": query})
    response = await model.ainvoke(prompt)

    return {
        "query": response.content,
        "iteration_count": iteration_count + 1,
    }

async def grade_documents(state: RAGState) -> Literal["generate_answer", "rewrite_question"]:
    """
    Decide next step after retrieval:
      - If docs are relevant        → generate_answer
      - If docs are irrelevant AND iterations remaining → rewrite_question (loop)
      - If max iterations hit       → generate_answer anyway (fail-safe)
    """
    LOGGER.info("Inside Grade Documents")
    question = state.get("query", "")
    retrieved_docs = state.get("retrieved_docs", [])
    iteration_count = state.get("iteration_count", 0)
    model = get_model()

    # Fail-safe: if we've rewritten too many times, just generate with what we have
    if iteration_count >= MAX_REWRITE_ITERATIONS:
        return "generate_answer"

    # If no docs were retrieved at all, no point grading — rewrite
    if not retrieved_docs:
        return "rewrite_question"

    prompt = GRADE_PROMPT.invoke({
        "question": question,
        "context": "\n".join(retrieved_docs),
    })
    structured_model = model.with_structured_output(GradeDocuments.model_json_schema())
    response = await structured_model.ainvoke(prompt)

    if response["binary_score"] == "yes":
        return "generate_answer"
    
    return "rewrite_question"