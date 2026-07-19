"""Command-line interface.

Python twin of ``apps/cli`` (Rust): build/query/search plus ``ask``, which
runs the full LLM pipeline the Rust CLI only prints a prompt for.

Run as ``python -m thinkingos.cli`` or via the ``thinkingos`` entry point.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from .config import Config
from .engine import Engine
from .utils import truncate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="thinkingos",
        description="ThinkingOS Python prototype — event-sourced reasoning over a markdown vault.",
    )
    parser.add_argument(
        "--vault",
        type=Path,
        default=None,
        help="vault directory (default: current directory or $THINKINGOS_VAULT)",
    )
    parser.add_argument(
        "--provider",
        choices=["echo", "ollama", "anthropic"],
        default=None,
        help="LLM provider (default: echo or $THINKINGOS_PROVIDER)",
    )
    parser.add_argument("--model", default=None, help="model name for the provider")

    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="ingest all markdown files in the vault")
    build.set_defaults(func=_cmd_build)

    query = sub.add_parser("query", help="traverse the graph from a concept")
    query.add_argument("concept")
    query.add_argument("--depth", type=int, default=2)
    query.set_defaults(func=_cmd_query)

    search = sub.add_parser("search", help="keyword search over the graph")
    search.add_argument("query")
    search.set_defaults(func=_cmd_search)

    ask = sub.add_parser("ask", help="answer a question using the reasoning pipeline")
    ask.add_argument("question")
    ask.add_argument(
        "--adversarial",
        action="store_true",
        help="run an adversarial critique + revision pass on the draft",
    )
    ask.add_argument(
        "--show-context",
        action="store_true",
        help="print the retrieved context graph before the answer",
    )
    ask.set_defaults(func=_cmd_ask)

    history = sub.add_parser("history", help="show the immutable event log")
    history.set_defaults(func=_cmd_history)

    return parser


def _config_from_args(args: argparse.Namespace) -> Config:
    config = Config.from_env()
    if args.vault is not None:
        config = replace(config, vault=args.vault)
    if args.provider is not None:
        config = replace(config, provider=args.provider)
    if args.model is not None:
        config = replace(config, model=args.model)
    if getattr(args, "adversarial", False):
        config = replace(config, adversarial=True)
    return config


def _cmd_build(engine: Engine, config: Config, args: argparse.Namespace) -> int:
    files, nodes, edges = engine.ingest_vault(config.vault)
    print(f"✅ Built {files} files | {nodes} new nodes | {edges} new edges")
    print(f"   Event log: {config.log_path} ({len(engine.store.log)} events)")
    return 0


def _cmd_query(engine: Engine, config: Config, args: argparse.Namespace) -> int:
    print(f"🔍 Traversing graph from: '{args.concept}'")
    start = engine.store.graph.find_by_content(args.concept)
    if start is None:
        print("   (concept not found — run `build` first?)")
        return 1
    for i, node in enumerate(engine.store.graph.traverse(start.id, args.depth), 1):
        print(f"  ↳ [{i}] ({node.node_type.value}) {truncate(node.content, 100)}")
    return 0


def _cmd_search(engine: Engine, config: Config, args: argparse.Namespace) -> int:
    print(f"⚡ Keyword search for: '{args.query}'")
    for i, (node, score) in enumerate(engine.store.graph.search(args.query), 1):
        print(f"  ↳ [{i}] (score: {score:.2f}) {truncate(node.content, 100)}")
    return 0


def _cmd_ask(engine: Engine, config: Config, args: argparse.Namespace) -> int:
    print(f"🧠 Reasoning over vault: {config.vault.resolve()}")
    print(f"   Provider: {engine.provider.name} | Plan: "
          + " → ".join(s.kind.value for s in engine.planner.plan(args.question).steps))
    result = engine.ask(args.question)

    if args.show_context:
        from .prompts import render_context

        print("\n---------------- CONTEXT GRAPH ----------------")
        if result.context.is_empty():
            print("(no relevant context found in vault)")
        else:
            print(render_context(result.context))

    print("\n------------------- ANSWER --------------------")
    print(result.answer)
    print("-----------------------------------------------")
    if result.critiques:
        verdict = "passed" if result.critiques[-1].passed else "revised after critique"
        print(f"🛡  Adversarial review: {verdict}")
    return 0


def _cmd_history(engine: Engine, config: Config, args: argparse.Namespace) -> int:
    events = engine.store.history()
    if not events:
        print("(event log is empty)")
        return 0
    for event in events:
        summary = truncate(str(dict(event.payload)), 80)
        print(f"  [{event.sequence:04d}] {event.timestamp} {event.kind:16s} {summary}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = _config_from_args(args)
    engine = Engine.from_config(config)
    return args.func(engine, config, args)


if __name__ == "__main__":
    sys.exit(main())
