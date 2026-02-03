import os

from constants.log import LOGGER
from constants.params import RAGState


async def retrieval_node(state: RAGState, config):
    LOGGER.info("Inside Retrieval Node")
    index = config["configurable"]["index_pinecone"]
    query = state.get('query', '')

    results = index.search(
        namespace=os.getenv("PINECONE_NAMESPACE"),
        query={
                "inputs": {"text": query}, 
                "top_k": 10
            },
            fields=["text", "text_answer"]
    )

    retrieved_docs = [hit['fields']['text_answer'] for hit in results['result']['hits']]
    return {"retrieved_docs": retrieved_docs}