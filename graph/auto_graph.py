# graph/auto_graph.py
from langgraph.graph import StateGraph, START, END
from graph.state import AutoState
from graph.routes import route_auto_review

# Import the exact files present in nodes/auto/
from nodes.auto.auto_context_node import auto_context_node
from nodes.auto.generate_search_query_node import generate_search_query_node
from nodes.auto.search_node import search_node
from nodes.auto.generate_doc_node import generate_doc_node
from nodes.auto.auto_review_node import auto_review_node
from nodes.auto.summary_memory_extraction_node import summary_memory_extraction_node

# Global alert node
from nodes.notify_user_node import notify_user_node

# 1. Initialize with AutoState
auto_builder = StateGraph(AutoState)

# 2. Add the 6 core local files + notification endpoint
auto_builder.add_node("auto_context_node", auto_context_node)
auto_builder.add_node("generate_search_query_node", generate_search_query_node)
auto_builder.add_node("search_node", search_node)
auto_builder.add_node("generate_doc_node", generate_doc_node)
auto_builder.add_node("auto_review_node", auto_review_node)
auto_builder.add_node("summary_memory_extraction_node", summary_memory_extraction_node)
auto_builder.add_node("notify_user_node", notify_user_node)

# ====================================================================
# 🚀 STREAMLINED GRAPH EDGES
# ====================================================================

auto_builder.add_edge(START, "auto_context_node")
auto_builder.add_edge("auto_context_node", "generate_search_query_node")
auto_builder.add_edge("generate_search_query_node", "search_node")
auto_builder.add_edge("search_node", "generate_doc_node")
auto_builder.add_edge("generate_doc_node", "auto_review_node")

# Conditional Router Evaluation
auto_builder.add_conditional_edges(
    "auto_review_node",
    route_auto_review,
    {
        "search_node": "search_node",                           # Loop back for deeper info
        "summary_memory_extraction_node": "summary_memory_extraction_node" # Approved path
    }
)

# Core extraction feeds into the user dashboard ping
auto_builder.add_edge("summary_memory_extraction_node", "notify_user_node")
auto_builder.add_edge("notify_user_node", END)

# Compile the final lean automated pipeline
compiled_auto_graph = auto_builder.compile()