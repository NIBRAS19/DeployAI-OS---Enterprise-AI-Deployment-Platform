"""Embedding generation, behind a small provider interface.

The default implementation is dependency-free and fully deterministic, so
retrieval works offline with zero external calls or model downloads. It uses
feature hashing (the "hashing trick"): each word is hashed into one of N
buckets, weighted by term frequency, then L2-normalized. Text that shares
vocabulary lands close together under cosine similarity — a real, working
technique, just a much weaker one than a trained embedding model.

Swap in a real provider (Voyage AI, OpenAI, Cohere, etc.) for production-
grade semantic search by implementing EmbeddingProvider and returning it
from get_embedding_provider() below; nothing else in the RAG pipeline needs
to change.
"""

import hashlib
import math
import re
from abc import ABC, abstractmethod

_WORD_RE = re.compile(r"[a-zA-Z0-9']+")


class EmbeddingProvider(ABC):
    dimensions: int

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        ...


class LocalHashEmbedding(EmbeddingProvider):
    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for word in _WORD_RE.findall(text.lower()):
            # hashlib (not builtin hash()) so buckets are stable across
            # processes — builtin string hashing is randomized per-run.
            bucket = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % self.dimensions
            vector[bucket] += 1.0
        norm = math.sqrt(sum(component * component for component in vector))
        if norm > 0:
            vector = [component / norm for component in vector]
        return vector


def get_embedding_provider() -> EmbeddingProvider:
    return LocalHashEmbedding()
