"""Pluggable LLM providers.

Prototype of ``crates/ai``: a minimal provider protocol plus implementations.
Providers are injected into the engine — nothing else imports them directly,
so swapping Ollama/Anthropic/OpenAI (or the future Rust binding) is a one-line
change at composition time.

Only the standard library is used; HTTP providers speak plain JSON over
``urllib`` to avoid SDK lock-in the Rust port would not share.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class ProviderError(RuntimeError):
    """Raised when a provider cannot produce a completion."""


class LLMProvider(Protocol):
    """The one seam between ThinkingOS and any language model."""

    name: str

    def complete(self, system: str, prompt: str) -> str:
        """Return the model's answer for ``prompt`` under ``system``."""
        ...


@dataclass
class EchoProvider:
    """Offline fallback: deterministically summarizes the compiled context.

    Keeps the whole pipeline runnable (and testable) with no API key, no
    network, and no nondeterminism.
    """

    name: str = "echo"

    def complete(self, system: str, prompt: str) -> str:
        return (
            "[echo provider — no LLM configured]\n"
            "The reasoning pipeline compiled the following prompt and would "
            "stream it to a real model:\n\n"
            f"--- system ---\n{system}\n\n--- prompt ---\n{prompt}"
        )


@dataclass
class OllamaProvider:
    """Local Ollama server (http://localhost:11434 by default)."""

    model: str = "llama3.2"
    base_url: str = "http://localhost:11434"
    timeout: float = 120.0
    name: str = "ollama"

    def complete(self, system: str, prompt: str) -> str:
        body = json.dumps(
            {
                "model": self.model,
                "system": system,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderError(f"ollama unreachable at {self.base_url}: {exc}") from exc
        return payload.get("response", "")


@dataclass
class AnthropicProvider:
    """Anthropic Messages API via plain HTTP."""

    model: str = "claude-sonnet-5"
    api_key: str | None = None
    max_tokens: int = 1024
    timeout: float = 120.0
    name: str = "anthropic"

    def complete(self, system: str, prompt: str) -> str:
        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ProviderError("ANTHROPIC_API_KEY is not set")
        body = json.dumps(
            {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(f"anthropic API error {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderError(f"anthropic unreachable: {exc}") from exc
        blocks = payload.get("content", [])
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def build_provider(name: str, model: str | None = None) -> LLMProvider:
    """Provider factory keyed by config name."""
    if name == "echo":
        return EchoProvider()
    if name == "ollama":
        return OllamaProvider(model=model or OllamaProvider.model)
    if name == "anthropic":
        return AnthropicProvider(model=model or AnthropicProvider.model)
    raise ProviderError(f"unknown provider: {name!r}")
