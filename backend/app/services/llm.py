from __future__ import annotations

import os
from typing import List, Dict, Any, Protocol, runtime_checkable, Optional


@runtime_checkable
class LLMProvider(Protocol):
    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        ...


class FakeLLMProvider:
    """Simple fake LLM used for tests. It answers using the provided context.

    It expects the prompt to contain a 'CONTEXT:' section followed by chunks.
    """

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        # naive: extract lines after 'CONTEXT:' and echo them as the answer
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
            raise RuntimeError("openai package required for OpenAIProvider") from e
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        response = self.client.responses.create(
            model=self.model, input=prompt, max_output_tokens=max_tokens
        )
        return response.output_text.strip()


def get_provider() -> LLMProvider:
    p = os.environ.get("LLM_PROVIDER", "fake").lower()
    if p == "openai":
        return OpenAIProvider()
    return FakeLLMProvider()
