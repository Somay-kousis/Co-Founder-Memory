# tools/github_tool.py
import requests

def query_public_github_repo(repo_path: str) -> str:
    """
    Queries public GitHub repository data completely for free using the open REST API.
    Expects format: 'owner/repo' (e.g., 'facebook/react')
    """
    clean_repo = repo_path.strip().replace("https://github.com/", "")
    url = f"https://api.github.com/repos/{clean_repo}"
    
    print(f"🐙 GitHub Tool: Fetching public metrics for {clean_repo}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            summary = (
                f"GitHub Repository: {data.get('full_name')}\n"
                f"Description: {data.get('description')}\n"
                f"Stars: {data.get('stargazers_count')} | Open Issues: {data.get('open_issues_count')}\n"
                f"Primary Language: {data.get('language')}"
            )
            return summary
        else:
            return f"Could not pull GitHub repo info. Status code: {response.status_code}"
    except Exception as e:
        return f"GitHub tool failure: {str(e)}"