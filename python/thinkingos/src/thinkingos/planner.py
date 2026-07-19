"""Reasoning pipeline planner.

Turns a question into an explicit, inspectable plan: an ordered list of steps
the engine executes. Steps are data, not behaviour — the engine owns execution
— so plans serialize cleanly and the Rust port can replay them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StepKind(str, Enum):
    RETRIEVE = "RETRIEVE"  # search graph + traverse neighborhood
    DRAFT = "DRAFT"  # generate an answer from context
    CRITIQUE = "CRITIQUE"  # adversarial review of the draft
    REVISE = "REVISE"  # rewrite the draft addressing the critique


@dataclass(frozen=True)
class Step:
    kind: StepKind
    description: str


@dataclass(frozen=True)
class Plan:
    question: str
    steps: tuple[Step, ...]


@dataclass(frozen=True)
class Planner:
    """Deterministic planner: same question + settings → same plan."""

    adversarial: bool = True
    max_revisions: int = 1

    def plan(self, question: str) -> Plan:
        steps: list[Step] = [
            Step(StepKind.RETRIEVE, "search the knowledge graph and expand neighborhood"),
            Step(StepKind.DRAFT, "draft an answer grounded in the retrieved context"),
        ]
        if self.adversarial:
            for _ in range(self.max_revisions):
                steps.append(Step(StepKind.CRITIQUE, "adversarially review the draft"))
                steps.append(Step(StepKind.REVISE, "revise the draft if the critique found problems"))
        return Plan(question=question, steps=tuple(steps))
