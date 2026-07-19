"""Immutable knowledge graph.

Prototype of ``crates/graph`` + the traversal in ``crates/storage``.
The graph is a persistent value: ``with_node`` / ``with_edge`` return new
graphs, so every point in reasoning history remains addressable.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Iterable, Mapping

from .models import Edge, Node, NodeType


def _frozen(mapping: Mapping) -> Mapping:
    return MappingProxyType(dict(mapping))


@dataclass(frozen=True)
class KnowledgeGraph:
    """Nodes + typed edges, with simple index structures for traversal."""

    nodes: Mapping[str, Node] = field(default_factory=lambda: _frozen({}))
    edges: Mapping[str, Edge] = field(default_factory=lambda: _frozen({}))

    # -- construction -------------------------------------------------------

    def with_node(self, node: Node) -> "KnowledgeGraph":
        nodes = dict(self.nodes)
        nodes[node.id] = node
        return replace(self, nodes=_frozen(nodes))

    def with_edge(self, edge: Edge) -> "KnowledgeGraph":
        edges = dict(self.edges)
        edges[edge.id] = edge
        return replace(self, edges=_frozen(edges))

    # -- lookup -------------------------------------------------------------

    def get_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Edge | None:
        return self.edges.get(edge_id)

    def find_by_content(self, content: str) -> Node | None:
        """Exact-content lookup (mirrors the entry query in ``storage::query_graph``)."""
        lowered = content.lower()
        for node in self.nodes.values():
            if node.content.lower() == lowered:
                return node
        return None

    def nodes_of_type(self, node_type: NodeType) -> list[Node]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    # -- traversal ----------------------------------------------------------

    def neighbors(self, node_id: str) -> list[tuple[Edge, Node]]:
        """Undirected adjacency: (edge, other-endpoint) pairs."""
        out: list[tuple[Edge, Node]] = []
        for edge in self.edges.values():
            other_id = None
            if edge.source_id == node_id:
                other_id = edge.target_id
            elif edge.target_id == node_id:
                other_id = edge.source_id
            if other_id is not None:
                other = self.nodes.get(other_id)
                if other is not None:
                    out.append((edge, other))
        return out

    def traverse(self, start_id: str, depth: int = 2) -> list[Node]:
        """Breadth-first neighborhood, mirroring ``storage::query_graph``.

        Returns nodes in deterministic BFS order, excluding the start node.
        """
        if start_id not in self.nodes:
            return []
        seen = {start_id}
        frontier = [start_id]
        result: list[Node] = []
        for _ in range(depth):
            next_frontier: list[str] = []
            for node_id in frontier:
                for _edge, other in self.neighbors(node_id):
                    if other.id not in seen:
                        seen.add(other.id)
                        result.append(other)
                        next_frontier.append(other.id)
            frontier = next_frontier
        return result

    # -- search -------------------------------------------------------------

    def search(self, query: str, limit: int = 10) -> list[tuple[Node, float]]:
        """Keyword scoring over node content (stand-in for FTS5 in Rust).

        Score = fraction of query terms present in the node content; ties
        broken by preferring shorter (more focused) nodes.
        """
        terms = [t for t in _tokenize(query) if t]
        if not terms:
            return []
        scored: list[tuple[Node, float]] = []
        for node in self.nodes.values():
            content_tokens = set(_tokenize(node.content))
            hits = sum(1 for t in terms if t in content_tokens)
            if hits:
                scored.append((node, hits / len(terms)))
        scored.sort(key=lambda pair: (-pair[1], len(pair[0].content), pair[0].id))
        return scored[:limit]


def _tokenize(text: str) -> Iterable[str]:
    cleaned = "".join(c.lower() if c.isalnum() else " " for c in text)
    return cleaned.split()
