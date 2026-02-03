import os

from pinecone import Pinecone
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from services.nodes import RAG_GRAPH


@tool
async def rag_search(query: str) -> str:
    """
    Use this tool to answer questions by searching the knowledge base.
    Retrieves relevant documents and generates an answer based on them.

    Args:
        query: The user's question to look up in the knowledge base.

    Returns:
        A generated answer based on retrieved documents.
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_HOST"))

    current_state = {
        "query": query,
        "messages": HumanMessage(query)
    }
    
    config = {
        "configurable": {
            "index_pinecone": index,
        },
    }
    
    response = await RAG_GRAPH.ainvoke(current_state, config)

    return response["final_answer"]