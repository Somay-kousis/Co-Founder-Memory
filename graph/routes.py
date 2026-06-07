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
    if not state.get("plan_ready") and state.get("plan_review_count", 0) < 5:
        return "plan_review_node"

    return "plan_finalize_node"

def route_auto_review(state: AutoState):
    if state["auto_ready"]:
        return "auto_summary_node"

    if state["needs_more_search"]:
        return "search_node"

    if state["needs_better_words"]:
        return "report_node"

    return END