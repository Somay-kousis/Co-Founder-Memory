from langgraph.graph import END
from graph.state import ManualState, AutoState


def route_query(state: ManualState):
    query_type = state["query_type"]

    if query_type == "ask":
        return "ask_retrieval_decision_node"

    if query_type == "memory":
        return "generate_memory_node"

    if query_type == "planning":
        return "planning_node"

    return END


def route_plan_review(state: ManualState):
    if not state["plan_ready"] and state["plan_review_count"] < 5:
        return "plan_review_node"

    return "final_response_node"


def route_memory_worthy(state: ManualState):
    if state["is_memory_worthy"]:
        return "memory_intent_classifier_node"

    return END


def route_memory_intent(state: ManualState):
    memory_intent = state["memory_intent"]

    if memory_intent == "add":
        return "add_memory_node"

    if memory_intent == "update":
        return "update_memory_node"

    if memory_intent == "delete":
        return "delete_memory_node"

    return END


def route_auto_review(state: AutoState):
    if state["auto_ready"]:
        return "auto_summary_node"

    if state["needs_more_search"]:
        return "search_node"

    if state["needs_better_words"]:
        return "report_node"

    return END

def route_ask_retrieval(state):
    if state["ask_retrieval_decision"]:
        return "ask_rag_node"
    return "ask_node"