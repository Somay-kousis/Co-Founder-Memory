from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    # Downloads a highly optimized, small local model (approx 130MB)
    # It runs completely locally with no API keys required
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )