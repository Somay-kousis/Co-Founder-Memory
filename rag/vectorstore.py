# rag/vectorstore.py
import os
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import create_client
from rag.embeddings import get_embeddings

def get_vectorstore():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        print("Vectorstore: Using persistent Supabase pgvector.")
        client = create_client(supabase_url, supabase_key)
        # Default table is "documents" and query_name is "match_documents"
        return SupabaseVectorStore(
            client=client,
            embedding=get_embeddings(),
            table_name="documents",
            query_name="match_documents"
        )
    else:
        # Fallback to local Chroma DB
        print("Vectorstore: Supabase credentials missing. Falling back to Chroma.")
        from langchain_community.vectorstores import Chroma
        persist_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db"))
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=get_embeddings()
        )