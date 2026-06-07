import os
from rag.loader import load_and_split_docs
from rag.embeddings import get_embeddings
from langchain_community.vectorstores import Chroma

def main():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db"))
    
    if not os.path.exists(data_path) or not os.listdir(data_path):
        print(f"Please put some Markdown (.md) files into the '{data_path}' directory first.")
        return

    print("Loading and splitting local documents...")
    chunks = load_and_split_docs()
    
    print(f"Embedding {len(chunks)} chunks and saving to local database ({db_path})...")
    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=db_path
    )
    print("Ingestion complete! Local DB is ready to use.")

if __name__ == "__main__":
    main()