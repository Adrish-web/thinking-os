"""Markdown → semantic IR.

Python mirror of ``crates/parser``: extracts ``[[wikilinks]]`` and
``relation:: [[target]]`` markers, producing the same content-addressed node
and edge ids as the Rust implementation (same sha256 seeds, same prefixes).
"""

from __future__ import annotations

import re

from .models import Edge, Node, NodeType
from .ontology import EdgeType, edge_type_for_relation
from .utils import generate_id

WIKILINK_RE = re.compile(r"\[\[(.*?)\]\]")
RELATION_RE = re.compile(r"([a-z_]+)::\s*\[\[(.*?)\]\]", re.IGNORECASE)

# Debug-format names used in Rust's edge-id seed (format!("{:?}", edge_type)).
_RUST_DEBUG_NAMES = {
    EdgeType.CAUSES: "Causes",
    EdgeType.SUPPORTS: "Supports",
    EdgeType.ANSWERS: "Answers",
    EdgeType.RELATED_TO: "RelatedTo",
    EdgeType.CONTAINS: "Contains",
    EdgeType.PART_OF: "PartOf",
    EdgeType.CONTRADICTS: "Contradicts",
    EdgeType.DERIVED_FROM: "DerivedFrom",
    EdgeType.USES: "Uses",
}


def parse_markdown(file_path: str, content: str) -> tuple[list[Node], list[Edge]]:
    """Parse one markdown document into nodes and edges."""
    nodes: dict[str, Node] = {}
    edges: dict[str, Edge] = {}

    doc_id = generate_id("doc", file_path)
    nodes[doc_id] = Node(
        id=doc_id,
        node_type=NodeType.DOCUMENT,
        content=content,
        file_path=file_path,
    )

    for match in WIKILINK_RE.finditer(content):
        concept_name = match.group(1).strip()
        concept_id = generate_id("concept", concept_name)
        nodes.setdefault(
            concept_id,
            Node(
                id=concept_id,
                node_type=NodeType.CONCEPT,
                content=concept_name,
                file_path=file_path,
            ),
        )
        edge_id = generate_id("edge", f"{doc_id}{concept_id}")
        edges.setdefault(
            edge_id,
            Edge(
                id=edge_id,
                source_id=doc_id,
                target_id=concept_id,
                edge_type=EdgeType.CONTAINS,
            ),
        )

    for match in RELATION_RE.finditer(content):
        relation = match.group(1).lower()
        target_name = match.group(2).strip()
        target_id = generate_id("concept", target_name)
        edge_type = edge_type_for_relation(relation)
        nodes.setdefault(
            target_id,
            Node(
                id=target_id,
                node_type=NodeType.CONCEPT,
                content=target_name,
                file_path=file_path,
            ),
        )
        edge_id = generate_id(
            "edge_rel", f"{doc_id}{target_id}{_RUST_DEBUG_NAMES[edge_type]}"
        )
        edges.setdefault(
            edge_id,
            Edge(
                id=edge_id,
                source_id=doc_id,
                target_id=target_id,
                edge_type=edge_type,
            ),
        )

    return list(nodes.values()), list(edges.values())
