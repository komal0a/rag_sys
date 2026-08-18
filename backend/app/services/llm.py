from __future__ import annotations

import os
import logging
from typing import Protocol, runtime_checkable, Optional

import requests

logger = logging.getLogger(__name__)


@runtime_checkable
class LLMProvider(Protocol):
    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        ...


class FakeLLMProvider:
    """Simple fake LLM used for tests."""

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        if "CONTEXT:" in prompt:
            parts = prompt.split("CONTEXT:", 1)[1].strip()
            if not parts:
                return "I don't have enough information to answer that question."
            return f"Answer based on context: {parts.splitlines()[0][:200]}"
        return "I don't have enough information to answer that question."


class OpenAIProvider:
    def __init__(self, model: Optional[str] = None):
        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError(
                "openai package required for OpenAIProvider"
            ) from e

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=max_tokens,
            )
        except Exception:
            logger.exception("OpenAI request failed")
            raise

        return response.output_text.strip()


class OllamaProvider:
    """Local LLM provider using Ollama."""

    def __init__(self, model: Optional[str] = None):
        self.base_url = os.environ.get(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434",
        ).rstrip("/")

        self.model = model or os.environ.get(
            "OLLAMA_MODEL",
            "llama3.2:3b",
        )

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                    },
                },
                timeout=120,
            )

            response.raise_for_status()
            data = response.json()

            return data.get("response", "").strip()

        except Exception:
            logger.exception("Ollama request failed")
            raise


def get_provider() -> LLMProvider:
    provider = os.environ.get("LLM_PROVIDER", "fake").lower()

    if provider == "openai":
        return OpenAIProvider()

    if provider == "ollama":
        return OllamaProvider()

    return FakeLLMProvider()