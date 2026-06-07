# graph/routes.py
from langgraph.graph import END
from graph.state import ManualState, AutoState

def route_query(state: ManualState):
    query_type = state["query_type"]
    if query_type == "ask":
        return "ask_retrieval_decision_node"
    if query_type == "memory":
        return "user_memory_extraction_node"
    if query_type == "planning":
        return "planning_node"
    return END

def route_ask_retrieval(state: ManualState):
    if state["ask_retrieval_decision"]:
        return "ask_rag_node"
    return "ask_node"

def route_plan_review(state: ManualState):
    """
    Evaluates execution right after plan_review_node completes.
    """
    is_ready = state.get("plan_ready", False)
    loops_spent = state.get("plan_review_count", 0)

    if not is_ready and loops_spent < 5:
        print(f"🔄 Plan Rejected. Loop counter at {loops_spent}/5. Sending back to planning_node.")
        return "planning_node"

    if loops_spent >= 5:
        print("🚨 Loop execution safety threshold hit (Max 5 loops reached). Breaking loop.")
    else:
        print("🟢 Plan passed review verification.")
        
    return END

def route_auto_review(state: AutoState):
    """
    Streamlined Auto Review Router: 
    Matches the exact 6-file layout sitting inside nodes/auto/
    """
    # 1. Missing context/links found -> Loop back to tool search layer
    if state.get("needs_more_search", False):
        print("🔍 Auto Review Flagged: Context missing. Routing back to search_node.")
        return "search_node"

    # 2. Approved OR Loop Cap Hit -> Route straight to permanent timeline extraction
    print("🟢 Auto Review Passed: Content clean or ready. Routing to summary_memory_extraction_node.")
    return "summary_memory_extraction_node"