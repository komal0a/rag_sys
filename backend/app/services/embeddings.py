"""Embeddings stub and interface.

This module provides a simple, deterministic, dependency-free embedding
generator intended ONLY for local testing. It is NOT a semantic embedding
implementation and must be replaced by a real provider (OpenAI/Vertex/ONNX/etc.)
for production.

Interface:
- `generate_embeddings(texts: List[str], dim: int = 8) -> List[List[float]]`:
    Returns a list of `len(texts)` vectors each of length `dim` where each
    element is a float in [0, 1). The function is deterministic and fast and
    suitable for tests that assert shapes and persistence but not semantic
    similarity.
"""

import hashlib
from typing import List


def generate_embeddings(texts: List[str], dim: int = 8) -> List[List[float]]:
    """Deterministic test stub for embeddings.

    Keep this implementation for tests only. Replace with a real embedding
    provider implementation behind the same function signature in production.
    """
    out = []
    for t in texts:
        h = hashlib.sha256(t.encode("utf-8")).digest()
        vec = []
        for i in range(dim):
            start = (i * 4) % len(h)
            chunk = h[start:start + 4]
            v = int.from_bytes(chunk, "big") / 2 ** 32
            vec.append(v)
        out.append(vec)
    return out
