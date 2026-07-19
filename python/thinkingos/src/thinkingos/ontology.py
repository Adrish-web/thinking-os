"""Ontology rules.

Prototype of ``crates/ontology``: which edge types may connect which node
types, and the mapping from ``relation::`` markers in markdown to edge types
(the same table hardcoded in ``crates/parser``).
"""

from __future__ import annotations

from .models import Edge, EdgeType, Node, NodeType

# relation-marker → edge type, mirroring crates/parser's match arms.
RELATION_KEYWORDS: dict[str, EdgeType] = {
    "causes": EdgeType.CAUSES,
    "supports": EdgeType.SUPPORTS,
    "answers": EdgeType.ANSWERS,
    "contradicts": EdgeType.CONTRADICTS,
    "uses": EdgeType.USES,
    "part_of": EdgeType.PART_OF,
    "derived_from": EdgeType.DERIVED_FROM,
}


def edge_type_for_relation(relation: str) -> EdgeType:
    return RELATION_KEYWORDS.get(relation.lower(), EdgeType.RELATED_TO)


# Which (source, target) node-type pairs each edge type permits.
# None means "any node type".
_ALLOWED: dict[EdgeType, set[tuple[NodeType, NodeType]] | None] = {
    EdgeType.CONTAINS: None,
    EdgeType.PART_OF: None,
    EdgeType.RELATED_TO: None,
    EdgeType.CAUSES: None,
    EdgeType.USES: None,
    EdgeType.DERIVED_FROM: None,
    EdgeType.SUPPORTS: {
        (NodeType.EVIDENCE, NodeType.CLAIM),
        (NodeType.DOCUMENT, NodeType.CLAIM),
        (NodeType.DOCUMENT, NodeType.CONCEPT),
        (NodeType.CLAIM, NodeType.CLAIM),
    },
    EdgeType.CONTRADICTS: {
        (NodeType.EVIDENCE, NodeType.CLAIM),
        (NodeType.CLAIM, NodeType.CLAIM),
        (NodeType.DOCUMENT, NodeType.CLAIM),
    },
    EdgeType.ANSWERS: {
        (NodeType.DOCUMENT, NodeType.QUESTION),
        (NodeType.CLAIM, NodeType.QUESTION),
        (NodeType.CONCEPT, NodeType.QUESTION),
    },
}


def validate_edge(edge: Edge, source: Node, target: Node) -> list[str]:
    """Return a list of ontology violations (empty = valid)."""
    problems: list[str] = []
    allowed = _ALLOWED.get(edge.edge_type)
    if allowed is not None and (source.node_type, target.node_type) not in allowed:
        problems.append(
            f"edge {edge.edge_type.value} not permitted from "
            f"{source.node_type.value} to {target.node_type.value}"
        )
    if edge.source_id == edge.target_id:
        problems.append("self-loop edges are not permitted")
    return problems
