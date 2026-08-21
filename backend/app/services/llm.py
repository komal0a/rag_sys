from __future__ import annotations

import logging
import os
from typing import Optional, Protocol, runtime_checkable

import requests

logger = logging.getLogger(__name__)


@runtime_checkable
class LLMProvider(Protocol):
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        ...


class FakeLLMProvider:
    """Simple fake LLM used for tests."""

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        if "CONTEXT:" in prompt:
            parts = prompt.split("CONTEXT:", 1)[1].strip()

            if not parts:
                return "I don't have enough information to answer that question."

            return f"Answer based on context: {parts.splitlines()[0][:200]}"

        return "I don't have enough information to answer that question."


class GeminiProvider:
    """Gemini LLM provider."""

    def __init__(self, model: Optional[str] = None):
        try:
            from google import genai
        except Exception as exc:
            raise RuntimeError(
                "google-genai package required for GeminiProvider"
            ) from exc

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required when LLM_PROVIDER=gemini"
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model or os.environ.get(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

    def generate(self, prompt: str, max_tokens: int = 1500) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.2,
                },
            )

            text = getattr(response, "text", None)

            if not text:
                raise RuntimeError("Gemini returned an empty response")

            print("\n========== GEMINI RESPONSE ==========")
            print(repr(text))
            print("LENGTH:", len(text))
            print("=====================================\n")

            return text.strip()

        except Exception:
            logger.exception("Gemini request failed")
            raise


class OpenAIProvider:
    def __init__(self, model: Optional[str] = None):
        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError(
                "openai package required for OpenAIProvider"
            ) from exc

        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.environ.get(
            "LLM_MODEL",
            "gpt-4o-mini",
        )

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

    if provider == "gemini":
        return GeminiProvider()

    if provider == "openai":
        return OpenAIProvider()

    if provider == "ollama":
        return OllamaProvider()

    return FakeLLMProvider()