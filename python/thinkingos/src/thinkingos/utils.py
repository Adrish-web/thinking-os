"""Small shared helpers.

Deterministic ID generation mirrors ``crates/parser::generate_id`` so that
Python-produced nodes and Rust-produced nodes hash to the same identifiers.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Callable

# A clock is injected wherever "now" is needed so state transitions stay
# deterministic under test (mirrors how the Rust layer will take a clock).
Clock = Callable[[], str]


def utc_now() -> str:
    """Default clock: current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def generate_id(prefix: str, seed: str) -> str:
    """Deterministic content-addressed id: ``{prefix}_{sha256(seed)}``.

    Must stay byte-compatible with ``crates/parser::generate_id``.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return f"{prefix}_{digest}"


def truncate(text: str, limit: int = 200) -> str:
    """Single-line preview of ``text``, at most ``limit`` characters."""
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"
