# thinkingos (Python prototype)

Rapid-prototyping layer for ThinkingOS. The production engine lives in the
Rust crates under `crates/`; this package mirrors their APIs so validated
designs migrate cleanly.

## Install

```bash
cd python/thinkingos
pip install -e .
```

## Usage

```bash
# Ingest all markdown in a vault (writes an append-only event log)
python -m thinkingos.cli --vault ~/notes build

# Traverse / search the knowledge graph
python -m thinkingos.cli --vault ~/notes query "Warburg Effect"
python -m thinkingos.cli --vault ~/notes search "cancer metabolism"

# Full reasoning pipeline (echo provider by default; --provider ollama|anthropic)
python -m thinkingos.cli --vault ~/notes ask "Why is cancer metabolism altered?"
python -m thinkingos.cli --vault ~/notes ask --adversarial --provider ollama "..."

# Immutable reasoning history
python -m thinkingos.cli --vault ~/notes history
```

## Module ↔ crate mapping

| Python module | Rust crate |
|---|---|
| `models` | `semantic-ir` |
| `parser` | `parser` |
| `graph` | `graph` / `storage` traversal |
| `store` | `storage` (event-sourced) |
| `ontology` | `ontology` |
| `reasoning` | `reasoning` |
| `providers` | `ai` |
| `engine`, `cli` | `apps/cli` |

## Design notes

- **Event sourcing** — the only persisted state is an append-only JSONL event
  log; the graph is a pure fold (`store.replay`) over it.
- **Immutability** — nodes, edges, graphs, events, plans, and results are
  frozen dataclasses.
- **Dependency injection** — providers, planner, adversary, and clock are all
  injected; `Engine.from_config` is the single composition root.
- **Rust interop** — node/edge ids are `sha256`-content-addressed with the
  same seeds as `crates/parser`, and enums serialize with the same
  SCREAMING_SNAKE_CASE spellings as `crates/semantic-ir`.
