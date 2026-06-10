import hashlib
import math
import re
from typing import Iterable, List

from langchain_core.embeddings import Embeddings


class HashingEmbeddings(Embeddings):
    """
    Tiny deterministic embedding fallback for free-tier deploys.

    It avoids downloading a local model at boot, which keeps the Render free
    container much lighter. Use EMBEDDINGS_PROVIDER=huggingface locally if you
    want stronger semantic retrieval.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9_+#.-]+", text.lower())

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if not norm:
            return vector
        return [value / norm for value in vector]

    def embed_documents(self, texts: Iterable[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


def get_embeddings():
    import os

    provider = os.getenv("EMBEDDINGS_PROVIDER", "hash").lower()
    if provider in {"huggingface", "hf", "sentence-transformers"}:
        from langchain_huggingface import HuggingFaceEmbeddings

        # Downloads a small local model. Best for local development; heavier for
        # zero-cost web hosting containers.
        return HuggingFaceEmbeddings(
            model_name=os.getenv(
                "HUGGINGFACE_EMBEDDING_MODEL",
                "sentence-transformers/all-MiniLM-L6-v2",
            )
        )

    return HashingEmbeddings(
        dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "384"))
    )
