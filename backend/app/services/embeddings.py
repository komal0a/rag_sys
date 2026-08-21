"""Embedding provider abstraction used by ingestion and retrieval.

Supports local Ollama, Gemini, OpenAI, and a fake provider for tests.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, List, Optional, Protocol, Sequence, runtime_checkable

import requests
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", "768"))
OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL", "http://host.docker.internal:11434"
)
OLLAMA_EMBEDDING_MODEL = os.environ.get(
    "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"
)


@runtime_checkable
class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        ...


class FakeEmbeddingProvider:
    """Deterministic, dependency-free embeddings for unit tests only."""

    def __init__(self, dim: int = 8) -> None:
        self.dim = dim

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        result: List[List[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            result.append([
                int.from_bytes(
                    digest[(index * 4) % len(digest):(index * 4) % len(digest) + 4],
                    "big",
                ) / 2**32
                for index in range(self.dim)
            ])
        return result


class OllamaEmbeddingProvider:
    """Embeds text locally through Ollama's embedding HTTP API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        expected_dim: Optional[int] = None,
        timeout: int = 120,
    ) -> None:
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")
        self.model = model or OLLAMA_EMBEDDING_MODEL
        self.expected_dim = EMBEDDING_DIM if expected_dim is None else expected_dim
        self.timeout = timeout

    def _post(self, path: str, payload: dict[str, Any]) -> requests.Response:
        try:
            return requests.post(
                f"{self.base_url}{path}",
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Cannot reach Ollama at {self.base_url} for embedding model "
                f"'{self.model}': {exc}"
            ) from exc

    def _json(self, response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Ollama returned invalid JSON for embedding model '{self.model}'"
            ) from exc
        if not isinstance(data, dict):
            raise RuntimeError(
                f"Ollama returned an invalid response for model '{self.model}'"
            )
        return data

    def _raise_for_status(self, response: requests.Response) -> None:
        if response.ok:
            return
        try:
            detail = self._json(response).get("error")
        except RuntimeError:
            detail = response.text
        raise RuntimeError(
            f"Ollama embedding request for model '{self.model}' failed "
            f"({response.status_code}): {detail or 'unknown error'}."
        )

    def _validate(
        self, embeddings: Any, expected_count: int
    ) -> List[List[float]]:
        if not isinstance(embeddings, list) or len(embeddings) != expected_count:
            actual = (
                len(embeddings) if isinstance(embeddings, list)
                else "an invalid number of"
            )
            raise RuntimeError(
                f"Ollama returned {actual} embeddings for {expected_count} "
                f"input texts using '{self.model}'"
            )

        result: List[List[float]] = []
        for embedding in embeddings:
            if (
                not isinstance(embedding, list)
                or not embedding
                or not all(isinstance(value, (int, float)) for value in embedding)
            ):
                raise RuntimeError(
                    f"Ollama returned an invalid embedding for model '{self.model}'"
                )

            if len(embedding) != self.expected_dim:
                raise RuntimeError(
                    f"Ollama model '{self.model}' returned {len(embedding)} "
                    f"dimensions, but EMBEDDING_DIM is {self.expected_dim}."
                )

            result.append([float(value) for value in embedding])

        return result

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        inputs = list(texts)
        if not inputs:
            return []

        response = self._post(
            "/api/embed",
            {"model": self.model, "input": inputs},
        )

        if response.status_code == 404:
            embeddings = []

            for prompt in inputs:
                legacy = self._post(
                    "/api/embeddings",
                    {"model": self.model, "prompt": prompt},
                )
                self._raise_for_status(legacy)
                embeddings.append(self._json(legacy).get("embedding"))

            return self._validate(embeddings, len(inputs))

        self._raise_for_status(response)

        return self._validate(
            self._json(response).get("embeddings"),
            len(inputs),
        )


class GeminiEmbeddingProvider:
    """Embeds text using Google's Gemini embedding API."""

    def __init__(self, model: Optional[str] = None) -> None:
        try:
            from google import genai
        except Exception as exc:
            raise RuntimeError(
                "google-genai package required for GeminiEmbeddingProvider"
            ) from exc

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required when EMBEDDING_PROVIDER=gemini"
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model or os.environ.get(
            "GEMINI_EMBEDDING_MODEL",
            "gemini-embedding-001",
        )
        self.dim = EMBEDDING_DIM

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        inputs = list(texts)

        if not inputs:
            return []

        result: List[List[float]] = []

        for text in inputs:
            try:
                response = self.client.models.embed_content(
                    model=self.model,
                    contents=text,
                    config={
                        "output_dimensionality": self.dim,
                    },
                )
            except Exception as exc:
                raise RuntimeError(
                    f"Gemini embedding request failed for model "
                    f"'{self.model}': {exc}"
                ) from exc

            embeddings = getattr(response, "embeddings", None)

            if not embeddings:
                raise RuntimeError(
                    f"Gemini returned no embedding for model '{self.model}'"
                )

            embedding = embeddings[0].values

            if not embedding or len(embedding) != self.dim:
                actual = len(embedding) if embedding else 0
                raise RuntimeError(
                    f"Gemini returned {actual} dimensions, expected {self.dim}."
                )

            result.append([float(value) for value in embedding])

        return result


class OpenAIEmbeddingProvider:
    """OpenAI embedding provider retained for compatibility."""

    def __init__(
        self,
        model: Optional[str] = None,
        dim: Optional[int] = None,
    ) -> None:
        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError(
                "openai package required for OpenAIEmbeddingProvider"
            ) from exc

        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.environ.get(
            "EMBEDDING_MODEL",
            "text-embedding-3-small",
        )
        self.dim = dim or EMBEDDING_DIM

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=list(texts),
            model=self.model,
            dimensions=self.dim,
        )

        embeddings = [item.embedding for item in response.data]

        if any(len(embedding) != self.dim for embedding in embeddings):
            raise RuntimeError(
                f"Received embedding with unexpected dimension, expected {self.dim}"
            )

        return embeddings


def get_provider() -> EmbeddingProvider:
    provider = os.environ.get("EMBEDDING_PROVIDER", "ollama").lower()

    if provider == "ollama":
        return OllamaEmbeddingProvider()

    if provider == "gemini":
        return GeminiEmbeddingProvider()

    if provider == "fake":
        return FakeEmbeddingProvider(
            dim=int(os.environ.get("EMBEDDING_DIM", "8"))
        )

    if provider == "openai":
        return OpenAIEmbeddingProvider(
            model=os.environ.get("EMBEDDING_MODEL"),
            dim=EMBEDDING_DIM,
        )

    raise RuntimeError(f"Unsupported EMBEDDING_PROVIDER '{provider}'")


def generate_embeddings(
    texts: List[str],
    dim: Optional[int] = None,
) -> List[List[float]]:
    """Backward-compatible helper used by ingestion endpoint and tests."""
    provider = get_provider()

    if dim is not None and isinstance(provider, FakeEmbeddingProvider):
        provider = FakeEmbeddingProvider(dim=dim)

    return provider.embed_texts(texts)