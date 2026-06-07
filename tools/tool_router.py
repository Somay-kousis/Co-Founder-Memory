# tools/tool_router.py
from tools.web_search_tool import execute_free_web_search
from tools.github_tool import query_public_github_repo
from datetime import datetime

def tool_router_execution(tool_name: str, arguments: str) -> str:
    """
    Central router that receives strategic commands from background nodes 
    and targets our zero-cost tool suite.
    """
    t_name = tool_name.lower().strip()
    
    if "search" in t_name or "web" in t_name or "duckduckgo" in t_name:
        return execute_free_web_search(arguments)
        
    elif "github" in t_name or "git" in t_name:
        return query_public_github_repo(arguments)
        
    elif "calendar" in t_name or "time" in t_name or "date" in t_name:
        # Returns current calendar and system operational parameters for tracking
        now = datetime.now()
        return f"[Local System Calendar Resource] Today is {now.strftime('%A, %B %d, %Y')}. Time context: {now.strftime('%H:%M:%S')}."
        
    else:
        # Fallback to web search if the tool target is broad or ambiguous
        return execute_free_web_search(f"{tool_name} {arguments}")