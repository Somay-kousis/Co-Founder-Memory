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

    # If revisions are requested and we are under the 5-loop ceiling -> go back to planner
    if not is_ready and loops_spent < 5:
        print(f"🔄 Plan Rejected. Loop counter at {loops_spent}/5. Sending to planning_node.")
        return "planning_node"

    # If it is ready OR hard cap is reached -> break out completely
    if loops_spent >= 5:
        print("🚨 Loop execution safety threshold hit (Max 5 loops reached). Breaking loop.")
    else:
        print("🟢 Plan passed review verification.")
        
    return "plan_finalize_node"

def route_auto_review(state: AutoState):
    if state["auto_ready"]:
        return "auto_summary_node"
    if state["needs_more_search"]:
        return "search_node"
    if state["needs_better_words"]:
        return "report_node"
    return END