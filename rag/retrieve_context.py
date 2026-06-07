import os
from rag.vectorstore import get_vectorstore

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
            
    # Combine everything cleanly into a single injection string
    full_formatted_context = "\n".join(injected_context_lines)
    
    return {
        "formatted_context": full_formatted_context,
        "retrieved_context": [doc.page_content for doc in search_results] if 'search_results' in locals() else []
    }