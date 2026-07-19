"""Configuration.

One frozen dataclass assembled from defaults → environment → CLI flags.
No global config object: whoever composes the engine passes it in.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class Config:
    # Storage: append-only event log inside the vault directory.
    vault: Path = Path(".")
    log_name: str = "thinking.events.jsonl"

    # Provider selection ("echo", "ollama", "anthropic").
    provider: str = "echo"
    model: str | None = None

    # Pipeline behaviour.
    adversarial: bool = False
    max_revisions: int = 1

    @property
    def log_path(self) -> Path:
        return self.vault / self.log_name

    @classmethod
    def from_env(cls) -> "Config":
        """Environment overrides, all prefixed ``THINKINGOS_``."""
        cfg = cls()
        if vault := os.environ.get("THINKINGOS_VAULT"):
            cfg = replace(cfg, vault=Path(vault))
        if provider := os.environ.get("THINKINGOS_PROVIDER"):
            cfg = replace(cfg, provider=provider)
        if model := os.environ.get("THINKINGOS_MODEL"):
            cfg = replace(cfg, model=model)
        if adversarial := os.environ.get("THINKINGOS_ADVERSARIAL"):
            cfg = replace(cfg, adversarial=adversarial.lower() in {"1", "true", "yes"})
        return cfg
