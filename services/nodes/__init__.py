from langgraph.graph import END, StateGraph

from constants.config import PATH
from constants.params import RAGState
from services.nodes.retrieval import retrieval_node
from services.nodes.generate_answer import generate_answer
from services.nodes.query_enhancement import rewrite_question, grade_documents


def make_rag_graph():
    graph_builder = StateGraph(RAGState)

    # --- nodes ---
    graph_builder.add_node("rewrite_question", rewrite_question)
    graph_builder.add_node("retrieval_node", retrieval_node)
    graph_builder.add_node("generate_answer", generate_answer)

    # --- entry ---
    graph_builder.set_entry_point("rewrite_question")

    # --- edges ---
    # rewrite always goes to retrieval
    graph_builder.add_edge("rewrite_question", "retrieval_node")

    # after retrieval, grade decides: generate or loop back to rewrite
    graph_builder.add_conditional_edges("retrieval_node", grade_documents)

    # generation is the terminal node
    graph_builder.add_edge("generate_answer", END)

    graph = graph_builder.compile()
    graph.get_graph(xray=True).draw_mermaid_png(
        output_file_path=f"{PATH}/imgs/rag_graph.png",
        max_retries=5,
        retry_delay=2.0
    )

    return graph

RAG_GRAPH = make_rag_graph()