import os
from langchain_community.vectorstores import Chroma
from rag.embeddings import get_embeddings

def get_vectorstore():
    # Points to the 'db' folder at the root level of your project
    persist_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db"))
    
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=get_embeddings()
    )