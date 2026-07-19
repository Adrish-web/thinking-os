"""Adversarial review.

The critic half of the pipeline: takes a draft answer plus its context and
asks a (separate, injectable) provider to attack it. A critique of exactly
``OK`` means the draft survived.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import prompts
from .providers import LLMProvider
from .reasoning import ReasoningContext

PASS_TOKEN = "OK"


@dataclass(frozen=True)
class Critique:
    text: str

    @property
    def passed(self) -> bool:
        return self.text.strip() == PASS_TOKEN


@dataclass
class Adversary:
    """Reviews drafts with its own provider (may differ from the drafting one)."""

    provider: LLMProvider

    def review(self, question: str, draft: str, context: ReasoningContext) -> Critique:
        prompt = prompts.render_adversary_prompt(question, draft, context)
        text = self.provider.complete(prompts.ADVERSARY_SYSTEM_PROMPT, prompt)
        return Critique(text=text)
