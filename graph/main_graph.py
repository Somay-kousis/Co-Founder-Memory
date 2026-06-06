from routes import route_memory_intent, route_query, route_ask_review, route_memory_worthy, route_plan_review
from state import ManualState
from langgraph.graph import START, END, StateGraph

def build_main_graph():
    graph = StateGraph(ManualState)
    
    # Add Nodes

    graph.nodes()

    # Add Edges



    # Add conditional edges 