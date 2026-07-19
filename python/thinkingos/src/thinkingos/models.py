"""Core data model.

Python mirrors of ``crates/semantic-ir``: :class:`Node` and :class:`Edge` with
the same fields and serialized enum spellings (SCREAMING_SNAKE_CASE), so JSON
produced here round-trips through the Rust structs unchanged.

Everything is a frozen dataclass — reasoning history is immutable; "changing" a
node means emitting a new event that carries a replacement value.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping


class NodeType(str, Enum):
    """Mirrors ``semantic_ir::NodeType`` (serde SCREAMING_SNAKE_CASE)."""

    DOCUMENT = "DOCUMENT"
    CONCEPT = "CONCEPT"
    CLAIM = "CLAIM"
    EVIDENCE = "EVIDENCE"
    QUESTION = "QUESTION"
    SOURCE = "SOURCE"
    METHOD = "METHOD"


class EdgeType(str, Enum):
    """Mirrors ``semantic_ir::EdgeType`` (serde SCREAMING_SNAKE_CASE)."""

    CONTAINS = "CONTAINS"
    PART_OF = "PART_OF"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    ANSWERS = "ANSWERS"
    DERIVED_FROM = "DERIVED_FROM"
    RELATED_TO = "RELATED_TO"
    CAUSES = "CAUSES"
    USES = "USES"


@dataclass(frozen=True)
class Node:
    """A unit of knowledge. Field-compatible with ``semantic_ir::Node``."""

    id: str
    node_type: NodeType
    content: str
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    metadata: Mapping[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "node_type": self.node_type.value,
            "content": self.content,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Node":
        return cls(
            id=data["id"],
            node_type=NodeType(data["node_type"]),
            content=data["content"],
            file_path=data.get("file_path", ""),
            line_start=data.get("line_start", 0),
            line_end=data.get("line_end", 0),
            metadata=dict(data.get("metadata", {})),
        )

    def with_content(self, content: str) -> "Node":
        return replace(self, content=content)


@dataclass(frozen=True)
class Edge:
    """A typed relation between nodes. Field-compatible with ``semantic_ir::Edge``."""

    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Edge":
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=EdgeType(data["edge_type"]),
            weight=data.get("weight", 1.0),
        )
