"""ThinkingOS — Python prototype layer.

Rapid-iteration twin of the Rust crates in ``crates/``. APIs deliberately
mirror their future Rust counterparts:

=====================  =============================
Python module          Rust crate
=====================  =============================
``models``             ``semantic-ir``
``parser``             ``parser``
``graph``              ``graph`` / ``storage`` (traversal)
``store``              ``storage`` (event-sourced)
``ontology``           ``ontology``
``reasoning``          ``reasoning``
``providers``          ``ai``
``engine`` / ``cli``   ``apps/cli``
=====================  =============================
"""

from .config import Config
from .engine import AskResult, Engine
from .graph import KnowledgeGraph
from .models import Edge, EdgeType, Node, NodeType
from .store import Event, EventLog, Store

__version__ = "0.1.0"

__all__ = [
    "AskResult",
    "Config",
    "Edge",
    "EdgeType",
    "Engine",
    "Event",
    "EventLog",
    "KnowledgeGraph",
    "Node",
    "NodeType",
    "Store",
    "__version__",
]
