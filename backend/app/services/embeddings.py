"""Embedding provider abstraction.

This module exposes an `EmbeddingProvider` interface and two concrete
implementations:

- `FakeEmbeddingProvider`: deterministic, dependency-free stub used for unit
  tests and local development.
- `OpenAIEmbeddingProvider`: wraps OpenAI's embeddings API when
  `EMBEDDING_PROVIDER=openai` and `OPENAI_API_KEY` are set.

Selection is driven by the `EMBEDDING_PROVIDER` environment variable. The
provider exposes `embed_texts(texts: List[str]) -> List[List[float]]`.

The fake provider is intentionally lightweight and MUST NOT be mistaken for a
real semantic model.
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import List, Sequence, Protocol, runtime_checkable, Optional, Any


# Configuration
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "fake")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
# Default dimension for the common miniLM model. Can be overridden via env.
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", 384))


@runtime_checkable
class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        ...


class FakeEmbeddingProvider:
    """Deterministic, dependency-free embeddings for tests."""

    def __init__(self, dim: int = 8) -> None:
        self.dim = dim

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        out: List[List[float]] = []
        for t in texts:
            h = hashlib.sha256(t.encode("utf-8")).digest()
            vec: List[float] = []
            for i in range(self.dim):
                start = (i * 4) % len(h)
                chunk = h[start:start + 4]
                v = int.from_bytes(chunk, "big") / 2 ** 32
                vec.append(v)
            out.append(vec)
        return out


class OpenAIEmbeddingProvider:
    """OpenAI embedding provider.

    Requires `OPENAI_API_KEY` in environment and `openai` package installed.
    This implementation is intentionally minimal and used when `EMBEDDING_PROVIDER`
    is set to `openai`.
    """

    def __init__(self, model: Optional[str] = None, dim: Optional[int] = None) -> None:
        try:
            import openai
        except Exception as e:
            raise RuntimeError("openai package required for OpenAIEmbeddingProvider") from e
        self.openai = openai
        self.model = model or EMBEDDING_MODEL
        self.dim = dim or EMBEDDING_DIM

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        # measure latency for basic logging
        t0 = time.time()
        resp = self.openai.Embedding.create(input=list(texts), model=self.model)
        latency = time.time() - t0
        # OpenAI returns embeddings under `data` keyed by index
        embeddings: List[List[float]] = [d["embedding"] for d in resp["data"]]
        if any(len(e) != self.dim for e in embeddings):
            # Do not silently accept mismatched dims
            raise RuntimeError(f"Received embedding with unexpected dimension, expected {self.dim}")
        return embeddings


def get_provider() -> EmbeddingProvider:
    provider = EMBEDDING_PROVIDER.lower()
    if provider == "fake":
        return FakeEmbeddingProvider(dim=int(os.environ.get("EMBEDDING_DIM", 8)))
    if provider == "openai":
        return OpenAIEmbeddingProvider(model=os.environ.get("EMBEDDING_MODEL"), dim=int(os.environ.get("EMBEDDING_DIM", EMBEDDING_DIM)))
    # fallback to fake
    return FakeEmbeddingProvider(dim=int(os.environ.get("EMBEDDING_DIM", 8)))


# Backwards-compatible helper for small call sites in tests
def generate_embeddings(texts: List[str], dim: Optional[int] = None) -> List[List[float]]:
    p = get_provider()
    return p.embed_texts(texts)