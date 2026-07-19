"""Context retrieval.

Prototype of ``crates/reasoning``: given a question and a knowledge graph,
deterministically assemble the context an LLM is allowed to reason over.
Pure functions of (graph, question) — no I/O, no model calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .graph import KnowledgeGraph
from .models import Node, NodeType


@dataclass(frozen=True)
class ReasoningContext:
    """Everything retrieved for one question. Immutable snapshot."""

    question: str
    entry_nodes: tuple[tuple[Node, float], ...] = ()
    neighborhood: tuple[Node, ...] = ()

    def is_empty(self) -> bool:
        return not self.entry_nodes and not self.neighborhood


@dataclass(frozen=True)
class RetrievalConfig:
    max_entry_nodes: int = 5
    traversal_depth: int = 2
    max_neighborhood: int = 20


def retrieve_context(
    graph: KnowledgeGraph,
    question: str,
    config: RetrievalConfig = RetrievalConfig(),
) -> ReasoningContext:
    """Search for entry nodes, then expand the semantic neighborhood.

    Replaces the hardcoded concept extraction in the current Rust prototype:
    instead of guessing one concept, we traverse from every concept node that
    matched the question or is contained by a matching document.
    """
    entry = tuple(graph.search(question, limit=config.max_entry_nodes))

    seen: set[str] = {node.id for node, _ in entry}
    neighborhood: list[Node] = []
    for node, _score in entry:
        for neighbor in graph.traverse(node.id, depth=config.traversal_depth):
            if neighbor.id in seen:
                continue
            seen.add(neighbor.id)
            # Documents are already represented by entry nodes; the
            # neighborhood carries concepts/claims only, to keep prompts lean.
            if neighbor.node_type != NodeType.DOCUMENT:
                neighborhood.append(neighbor)
            if len(neighborhood) >= config.max_neighborhood:
                break
        if len(neighborhood) >= config.max_neighborhood:
            break

    return ReasoningContext(
        question=question,
        entry_nodes=entry,
        neighborhood=tuple(neighborhood),
    )
