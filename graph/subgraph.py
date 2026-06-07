# graph/subgraph.py
from langgraph.graph import StateGraph, START, END
from graph.state import SubGraphState
from nodes.subgraph_nodes.grade_documents_node import grade_documents_node
from nodes.subgraph_nodes.web_search_node import web_search_node
from nodes.subgraph_nodes.grade_generation_node import grade_generation_node

def route_subgraph_search(state: SubGraphState):
    """
    Determines if the document grading or generation layers 
    require an external DuckDuckGo backup query search hit.
    """
    if state.get("run_web_search", False):
        print("🔍 Subgraph Router: Flawed context detected. Routing to web_search_node.")
        return "web_search_node"
    
    print("🟢 Subgraph Router: Context verified and grounded. Exiting subgraph.")
    return END

# ---------------------------------------------------------
# GRAPH CONSTRUCTION & COMPILATION
# ---------------------------------------------------------

# 1. Initialize the graph with your state
subgraph_builder = StateGraph(SubGraphState)

# 2. Add your nodes to the graph
subgraph_builder.add_node("grade_documents_node", grade_documents_node)
subgraph_builder.add_node("web_search_node", web_search_node)
subgraph_builder.add_node("grade_generation_node", grade_generation_node)

# 3. Define the flow (adjust these edges based on your exact desired logic)
subgraph_builder.add_edge(START, "grade_documents_node")

# 4. Add the conditional routing
subgraph_builder.add_conditional_edges(
    "grade_documents_node",
    route_subgraph_search,
    {
        "web_search_node": "web_search_node",
        END: END
    }
)

# 5. Finish the routing for the web search path
subgraph_builder.add_edge("web_search_node", "grade_generation_node")
subgraph_builder.add_edge("grade_generation_node", END)

# 6. Compile the graph into the variable main_graph.py is looking for
compiled_rag_subgraph = subgraph_builder.compile()