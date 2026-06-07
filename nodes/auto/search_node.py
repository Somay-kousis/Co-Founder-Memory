# nodes/auto/search_node.py
from graph.state import AutoState
from tools.tool_router import tool_router_execution

def search_node(state: AutoState):
    """
    Auto Pipeline Layer: Takes generated queries and utilizes our 
    100% free tool infrastructure to gather targeted background info.
    """
    query_to_run = state.get("user_query") or "Hackathons 2026 engineering"
    print(f"🔍 Auto Search Node: Activating zero-cost tool pipelines for query: '{query_to_run}'")
    
    # 1. Execute the free tool router pipeline
    # It automatically decides to use DDG Search based on string conditions
    gathered_intelligence = tool_router_execution(tool_name="duckduckgo", arguments=query_to_run)
    
    # 2. Extract any active context lists and append our new intelligence assets
    current_context = state.get("retrieved_context") or []
    updated_context = current_context + [gathered_intelligence]
    
    print("🟢 Auto Search Node: Intelligence assets compiled and stored safely in state context.")
    
    return {
        "retrieved_context": updated_context,
        "needs_more_search": False  # Successfully handled, clear the flag!
    }