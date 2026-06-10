import os
import json
from rag.vectorstore import get_vectorstore


def _append_profile_context(lines: list[str]) -> None:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        return

    try:
        from supabase import create_client

        client = create_client(supabase_url, supabase_key)
        res = (
            client.table("memory_store")
            .select("value")
            .eq("key", "co_founder_profile")
            .execute()
        )
        profile = None
        for row in res.data or []:
            profile = row.get("value")
            break
        if not profile:
            return

        lines.append("--- PERMANENT SUPABASE PROFILE ---")
        for project in profile.get("projects", []):
            lines.append(
                f"Project: {project.get('name', 'Unnamed')} | "
                f"Status: {project.get('status', 'unknown')} | "
                f"Goal: {project.get('vision_goal', '')}"
            )
            for update in project.get("updates", [])[-3:]:
                lines.append(f"- Update: {update.get('summary', '')}")

        preferences = profile.get("preferences", {})
        tech_stack = preferences.get("tech_stack") or []
        if tech_stack:
            lines.append(f"Tech stack: {', '.join(tech_stack)}")

        for decision in profile.get("decisions", [])[-5:]:
            lines.append(
                f"Decision: {decision.get('title', 'Untitled')} - "
                f"{decision.get('context_why', '')}"
            )
    except Exception as exc:
        print(f"⚠️ Profile Retrieval Error: Permanent profile could not be reached. {exc}")
        lines.append("[Permanent Profile Context: Temporarily Unavailable]")

def retrieve_all_context(query: str, state_memories: list = None) -> dict:
    """
    Queries both the local vector database and extracts profile context, 
    returning raw context strings and list blocks for state updates.
    """
    injected_context_lines = []
    
    # 1. Vector DB (Chroma) RAG Retreival
    try:
        db = get_vectorstore()
        # Query the top 3 most semantically similar codebase chunks
        search_results = db.similarity_search(query, k=3)
        
        if search_results:
            injected_context_lines.append("--- LOCAL KNOWLEDGE BASE (RAG) ---")
            for i, doc in enumerate(search_results, 1):
                clean_content = doc.page_content.strip()
                source_meta = doc.metadata.get('source', 'unknown')
                injected_context_lines.append(f"[{i}] (Source: {os.path.basename(source_meta)})\n{clean_content}\n")
        else:
            injected_context_lines.append("[Vector RAG Documents: No matching chunks found]")
    except Exception as e:
        print(f"⚠️ RAG Retrieval Error: VectorDB could not be reached. {e}")
        injected_context_lines.append("[RAG Database Context: Temporarily Unavailable]")

    # 2. Permanent Memories Injection
    # We append memories passed in via state execution frames
    memories = state_memories or []
    if memories:
        injected_context_lines.append("--- PERMANENT USER PROFILE MEMORIES ---")
        for memory in memories:
            injected_context_lines.append(f"- {memory}")

    # 3. Durable Supabase profile. This is the actual long-term memory store
    # used in production, so ask/RAG answers should see it directly.
    _append_profile_context(injected_context_lines)
            
    # Combine everything cleanly into a single injection string
    full_formatted_context = "\n".join(injected_context_lines)
    
    return {
        "formatted_context": full_formatted_context,
        "retrieved_context": [doc.page_content for doc in search_results] if 'search_results' in locals() else []
    }
