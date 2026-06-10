# nodes/subgraph_nodes/web_search_node.py
from langchain_community.tools import DuckDuckGoSearchRun
from graph.state import SubGraphState

search_tool = None


def get_search_tool():
    global search_tool
    if search_tool is None:
        search_tool = DuckDuckGoSearchRun()
    return search_tool

def web_search_node(state: SubGraphState):
    """
    CRAG Fallback Layer: Executes a completely free web search query via 
    DuckDuckGo when local vector store documentation is insufficient.
    """
    query = state["user_query"]
    existing_context = state.get("retrieved_context") or []
    
    print(f"🌐 CRAG Fallback: Running free DDG Search for: '{query}'")
    
    try:
        search_result_text = get_search_tool().invoke(query)
        formatted_chunk = f"[Web Reference: DuckDuckGo Search Result]\n{search_result_text}"
        web_context_chunks = [formatted_chunk]
        print("🟢 CRAG Fallback: Successfully retrieved fresh results from DuckDuckGo.")
    except Exception as e:
        print(f"❌ CRAG Fallback Error: Free web search execution failed. {e}")
        web_context_chunks = ["[Web Search Fallback: DuckDuckGo Service Temporarily Down]"]

    return {
        "retrieved_context": existing_context + web_context_chunks,
        "run_web_search": False  # Successfully handled search, drop flag to avoid looping
    }
