# rag/injest.py
import os
from dotenv import load_dotenv
load_dotenv()

from rag.loader import load_and_split_docs
from rag.vectorstore import get_vectorstore

def main():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    
    if not os.path.exists(data_path) or not os.listdir(data_path):
        print(f"Please put some Markdown (.md) files into the '{data_path}' directory first.")
        return

    print("Loading and splitting local documents...")
    chunks = load_and_split_docs()
    
    print(f"Embedding and adding {len(chunks)} chunks to the vector store...")
    try:
        db = get_vectorstore()
        from langchain_community.vectorstores import SupabaseVectorStore
        if isinstance(db, SupabaseVectorStore):
            print("Target DB: Supabase pgvector.")
            # Clear old records to avoid duplication if running ingestion again
            try:
                print("Clearing existing documents in Supabase vector store...")
                db._client.table("documents").delete().neq("id", -1).execute()
            except Exception as delete_err:
                print(f"Warning: Could not clear existing documents: {delete_err}")
        else:
            print("Target DB: Local Chroma DB.")
            
        db.add_documents(chunks)
        print("Ingestion complete! Vector store is ready to use.")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")

if __name__ == "__main__":
    main()