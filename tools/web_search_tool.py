# tools/web_search_tool.py
from langchain_community.tools import DuckDuckGoSearchRun

search_engine = None


def get_search_engine():
    global search_engine
    if search_engine is None:
        search_engine = DuckDuckGoSearchRun()
    return search_engine

def execute_free_web_search(query: str) -> str:
    """Runs an unlimited, completely free web scan via DuckDuckGo."""
    print(f"🌐 Search Tool: Executing free DDG query for '{query}'...")
    try:
        results = get_search_engine().invoke(query)
        return f"[DuckDuckGo Live Intelligence Stream]\n{results}"
    except Exception as e:
        return f"Web search tool failed: {str(e)}"
