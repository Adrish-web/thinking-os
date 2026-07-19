"""Event-sourced storage.

The single source of truth is an append-only event log (JSONL on disk).
Knowledge-graph state is a pure fold over that log — never mutated in place.
This is the prototype of what the Rust ``storage`` crate will become once it
moves from row-updates (current SQLite impl) to event sourcing.

Layers:

* :class:`Event` — immutable record of one state transition.
* :class:`EventLog` — append-only persistence (in-memory or JSONL file).
* :func:`replay` — fold events into a :class:`~thinkingos.graph.KnowledgeGraph`.
* :class:`Store` — thin facade combining the two, the only API callers need.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from .graph import KnowledgeGraph
from .models import Edge, Node
from .utils import Clock, generate_id, utc_now

# Event kinds — deliberately a closed set, mirroring a future Rust enum.
NODE_ADDED = "NODE_ADDED"
EDGE_ADDED = "EDGE_ADDED"
QUESTION_ASKED = "QUESTION_ASKED"
ANSWER_RECORDED = "ANSWER_RECORDED"

EVENT_KINDS = frozenset({NODE_ADDED, EDGE_ADDED, QUESTION_ASKED, ANSWER_RECORDED})


@dataclass(frozen=True)
class Event:
    """One immutable entry in the reasoning history."""

    id: str
    kind: str
    payload: Mapping[str, Any]
    timestamp: str
    sequence: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "payload": dict(self.payload),
            "timestamp": self.timestamp,
            "sequence": self.sequence,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Event":
        return cls(
            id=data["id"],
            kind=data["kind"],
            payload=dict(data["payload"]),
            timestamp=data["timestamp"],
            sequence=data["sequence"],
        )


class EventLog:
    """Append-only event log. ``path=None`` keeps it purely in memory."""

    def __init__(self, path: Path | None = None, clock: Clock = utc_now) -> None:
        self._path = path
        self._clock = clock
        self._events: list[Event] = []
        if path is not None and path.exists():
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        self._events.append(Event.from_dict(json.loads(line)))

    def append(self, kind: str, payload: Mapping[str, Any]) -> Event:
        if kind not in EVENT_KINDS:
            raise ValueError(f"unknown event kind: {kind!r}")
        sequence = len(self._events)
        event = Event(
            id=generate_id("evt", f"{sequence}:{kind}:{json.dumps(payload, sort_keys=True)}"),
            kind=kind,
            payload=payload,
            timestamp=self._clock(),
            sequence=sequence,
        )
        self._events.append(event)
        if self._path is not None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
        return event

    def __iter__(self) -> Iterator[Event]:
        return iter(self._events)

    def __len__(self) -> int:
        return len(self._events)


def replay(events: Iterable[Event]) -> KnowledgeGraph:
    """Pure fold: events → graph state. Same events, same graph, always."""
    graph = KnowledgeGraph()
    for event in events:
        if event.kind == NODE_ADDED:
            graph = graph.with_node(Node.from_dict(event.payload))
        elif event.kind == EDGE_ADDED:
            graph = graph.with_edge(Edge.from_dict(event.payload))
        # QUESTION_ASKED / ANSWER_RECORDED are history, not graph structure.
    return graph


@dataclass
class Store:
    """Facade over the event log; the only storage API the rest of the code uses.

    The cached graph is an optimization — it is always equal to
    ``replay(self.log)`` and can be discarded and rebuilt at any time.
    """

    log: EventLog = field(default_factory=EventLog)

    def __post_init__(self) -> None:
        self._graph = replay(self.log)

    @classmethod
    def open(cls, path: Path, clock: Clock = utc_now) -> "Store":
        return cls(log=EventLog(path, clock=clock))

    @property
    def graph(self) -> KnowledgeGraph:
        return self._graph

    def add_node(self, node: Node) -> None:
        if self._graph.get_node(node.id) is not None:
            return  # idempotent: content-addressed ids make duplicates a no-op
        self.log.append(NODE_ADDED, node.to_dict())
        self._graph = self._graph.with_node(node)

    def add_edge(self, edge: Edge) -> None:
        if self._graph.get_edge(edge.id) is not None:
            return
        self.log.append(EDGE_ADDED, edge.to_dict())
        self._graph = self._graph.with_edge(edge)

    def record_question(self, question: str) -> None:
        self.log.append(QUESTION_ASKED, {"question": question})

    def record_answer(self, question: str, answer: str, provider: str) -> None:
        self.log.append(
            ANSWER_RECORDED,
            {"question": question, "answer": answer, "provider": provider},
        )

    def history(self) -> list[Event]:
        return list(self.log)
