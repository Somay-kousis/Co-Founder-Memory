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

    # If revisions are requested and we are under the 5-loop ceiling -> loop back
    if not is_ready and loops_spent < 5:
        print(f"🔄 Plan Rejected. Loop counter at {loops_spent}/5. Sending back to planning_node.")
        return "planning_node"

    # If it is ready OR hard cap is reached -> break out completely to END
    if loops_spent >= 5:
        print("🚨 Loop execution safety threshold hit (Max 5 loops reached). Breaking loop.")
    else:
        print("🟢 Plan passed review verification.")
        
    return END

def route_auto_review(state: AutoState):
    """
    Directs flow based on the Quality Control findings of the auto_review_node.
    Matches the Excalidraw white-board loop topology.
    """
    # 1. Content is pristine -> route straight to permanent day synthesis
    if state.get("auto_ready", False):
        print("🟢 Auto Review Passed: Content clean. Routing to auto_summary_node.")
        return "auto_summary_node"

    # 2. Missing info found -> send to tool search first, which steps into generate_doc_node next
    if state.get("needs_more_search", False):
        print("🔍 Auto Review Flagged: Context missing. Routing to search_node.")
        return "search_node"

    # 3. Text formatting is sloppy -> send to editing desk first, which steps into generate_doc_node next
    if state.get("needs_better_words", False):
        print("✍️ Auto Review Flagged: Sloppy syntax. Routing to report_node.")
        return "report_node"

    return "auto_summary_node"