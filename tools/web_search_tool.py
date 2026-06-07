# tools/web_search_tool.py
from langchain_community.tools import DuckDuckGoSearchRun

search_engine = DuckDuckGoSearchRun()

def execute_free_web_search(query: str) -> str:
    """Runs an unlimited, completely free web scan via DuckDuckGo."""
    print(f"🌐 Search Tool: Executing free DDG query for '{query}'...")
    try:
        results = search_engine.invoke(query)
        return f"[DuckDuckGo Live Intelligence Stream]\n{results}"
    except Exception as e:
        return f"Web search tool failed: {str(e)}"