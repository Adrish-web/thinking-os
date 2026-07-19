"""The engine: composition root and pipeline executor.

Everything else in this package is a small, injectable part; the engine wires
them together and executes plans step by step. Mirrors the role the top-level
Rust CLI + ``reasoning`` crate will play in production.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import prompts
from .adversary import Adversary, Critique
from .config import Config
from .parser import parse_markdown
from .planner import Plan, Planner, StepKind
from .providers import LLMProvider, build_provider
from .reasoning import ReasoningContext, RetrievalConfig, retrieve_context
from .store import Store


@dataclass(frozen=True)
class AskResult:
    """Full trace of one question through the pipeline."""

    question: str
    answer: str
    context: ReasoningContext
    plan: Plan
    critiques: tuple[Critique, ...] = ()
    provider: str = ""


@dataclass
class Engine:
    """Executes reasoning plans over an event-sourced knowledge graph.

    All collaborators are injected; :meth:`from_config` is the convenience
    composition root used by the CLI.
    """

    store: Store
    provider: LLMProvider
    planner: Planner = field(default_factory=Planner)
    adversary: Adversary | None = None
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)

    @classmethod
    def from_config(cls, config: Config) -> "Engine":
        provider = build_provider(config.provider, config.model)
        adversary = Adversary(provider=provider) if config.adversarial else None
        return cls(
            store=Store.open(config.log_path),
            provider=provider,
            planner=Planner(
                adversarial=config.adversarial,
                max_revisions=config.max_revisions,
            ),
            adversary=adversary,
        )

    # -- ingestion ----------------------------------------------------------

    def ingest_file(self, path: Path) -> tuple[int, int]:
        """Parse one markdown file into the graph. Returns (nodes, edges) added."""
        nodes, edges = parse_markdown(str(path), path.read_text(encoding="utf-8"))
        before_nodes = len(self.store.graph.nodes)
        before_edges = len(self.store.graph.edges)
        for node in nodes:
            self.store.add_node(node)
        for edge in edges:
            self.store.add_edge(edge)
        return (
            len(self.store.graph.nodes) - before_nodes,
            len(self.store.graph.edges) - before_edges,
        )

    def ingest_vault(self, vault: Path) -> tuple[int, int, int]:
        """Ingest every ``.md`` file under ``vault``. Returns (files, nodes, edges)."""
        files = 0
        nodes = 0
        edges = 0
        for path in sorted(vault.rglob("*.md")):
            added_nodes, added_edges = self.ingest_file(path)
            files += 1
            nodes += added_nodes
            edges += added_edges
        return files, nodes, edges

    # -- reasoning ----------------------------------------------------------

    def ask(self, question: str) -> AskResult:
        """Run the full plan for a question and record it in history."""
        self.store.record_question(question)
        plan = self.planner.plan(question)

        context = ReasoningContext(question=question)
        draft = ""
        critiques: list[Critique] = []

        for step in plan.steps:
            if step.kind is StepKind.RETRIEVE:
                context = retrieve_context(self.store.graph, question, self.retrieval)
            elif step.kind is StepKind.DRAFT:
                draft = self.provider.complete(
                    prompts.SYSTEM_PROMPT,
                    prompts.render_ask_prompt(question, context),
                )
            elif step.kind is StepKind.CRITIQUE:
                assert self.adversary is not None, "plan has CRITIQUE but no adversary"
                critiques.append(self.adversary.review(question, draft, context))
            elif step.kind is StepKind.REVISE:
                if critiques and not critiques[-1].passed:
                    draft = self.provider.complete(
                        prompts.SYSTEM_PROMPT,
                        prompts.render_revision_prompt(
                            question, draft, critiques[-1].text, context
                        ),
                    )

        self.store.record_answer(question, draft, self.provider.name)
        return AskResult(
            question=question,
            answer=draft,
            context=context,
            plan=plan,
            critiques=tuple(critiques),
            provider=self.provider.name,
        )
