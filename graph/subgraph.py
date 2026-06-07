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