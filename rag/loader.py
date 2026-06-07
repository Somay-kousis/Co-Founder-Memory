from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split_docs():
    loader = DirectoryLoader(
        "data", # Reads from the top-level 'data' directory seen in your screenshot
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1600,
        chunk_overlap=200,
    )

    return splitter.split_documents(docs)