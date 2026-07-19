# ThinkingOS

> **An open-source, local-first operating system for knowledge and reasoning.**

ThinkingOS is a knowledge engine designed to help people **understand, connect, and reason over information** rather than simply store it. It combines structured knowledge representation, semantic search, event sourcing, and optional AI-assisted reasoning into a unified platform for research and learning.

The project is built around a simple idea:

> **Knowledge compounds when it is connected. Intelligence emerges when those connections can be explored, questioned, and refined.**

---

# Why ThinkingOS?

Modern knowledge tools excel at collecting information but often leave the reasoning process to the user.

ThinkingOS aims to bridge that gap by providing infrastructure for:

* Building structured knowledge graphs from notes and documents
* Discovering semantic relationships between ideas
* Retrieving relevant context for complex questions
* Recording reasoning as reproducible, inspectable workflows
* Supporting AI-assisted synthesis without depending on proprietary services

The objective is not to replace human thinking, but to augment it.

---

# Design Principles

## Local-First

Your knowledge should remain under your control.

The core engine is designed to function entirely offline. Cloud-based language models are optional enhancements, not requirements.

---

## Open by Design

ThinkingOS is developed as an open-source platform with transparent architecture, extensible interfaces, and reproducible reasoning.

---

## Graph-Centric

Information is represented as interconnected entities rather than isolated documents.

Concepts, claims, evidence, questions, papers, and experiments become part of a navigable knowledge graph.

---

## Reproducible Reasoning

Every reasoning session can be recorded as an immutable sequence of events.

This enables provenance, auditability, replay, and continuous refinement.

---

## AI as an Enhancement

Large language models are treated as interchangeable providers rather than core dependencies.

Supported providers may include:

* Ollama (local)
* Anthropic Claude
* OpenAI
* Google Gemini
* Additional providers through a common interface

Without an AI provider, ThinkingOS still supports parsing, indexing, graph construction, search, traversal, and event management.

---

# Architecture

```text
                    ThinkingOS

                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
  Knowledge Infrastructure           AI Providers
         │                                   │
         │                       Ollama / Claude
         │                       OpenAI / Gemini
         │
 ┌─────────────────────────────────────────────────┐
 │ Markdown Parser                                 │
 │ Knowledge Graph                                 │
 │ Ontology                                        │
 │ Search & Retrieval                              │
 │ Event Store                                     │
 │ Planning & Reasoning                            │
 └─────────────────────────────────────────────────┘
```

The system separates **knowledge representation** from **reasoning**, allowing the core platform to evolve independently of any specific AI model.

---

# Repository Structure

```text
thinking-os/

├── crates/                 # Rust core libraries
│   ├── graph/
│   ├── ontology/
│   ├── reasoning/
│   ├── search/
│   ├── storage/
│   └── ...
│
├── apps/
│   ├── cli/
│   ├── web-dashboard/
│   ├── obsidian-plugin/
│   └── vscode-extension/
│
├── python/
│   └── thinkingos/
│       ├── src/
│       └── pyproject.toml
│
├── docs/
└── README.md
```

---

# Current Capabilities

The current prototype includes:

* Markdown document parsing
* Knowledge graph construction
* Graph traversal and keyword search
* Event-sourced knowledge history
* Modular reasoning pipeline
* Pluggable AI provider interface
* Python orchestration layer
* Rust core workspace

The project is under active development and APIs may evolve.

---

# Technology Stack

### Rust

Responsible for performance-critical infrastructure:

* Graph engine
* Storage
* Search
* Query execution
* Future production runtime

### Python

Used for:

* Rapid prototyping
* AI orchestration
* Research workflows
* Experimentation
* Integration with external tooling

The long-term architecture keeps Python focused on orchestration while Rust provides the production engine.

---

# Roadmap

### Phase 1 — Knowledge Infrastructure

* Markdown parsing
* Knowledge graph
* Search
* Event sourcing
* Command-line interface

### Phase 2 — Semantic Representation

* Typed ontology
* Claims
* Evidence
* Questions
* Papers
* Experiments
* Datasets

### Phase 3 — Reasoning Engine

* Multi-step planning
* Evidence retrieval
* Hypothesis generation
* Contradiction detection
* Knowledge synthesis

### Phase 4 — Integrations

* Interactive graph visualization
* Obsidian plugin
* VS Code extension
* Web interface
* MCP support

### Phase 5 — ThinkingOS

A complete platform for research, learning, writing, and scientific reasoning that remains local-first, extensible, and accessible.

---

# Contributing

ThinkingOS is in its early stages, and contributions are welcome.

Areas of interest include:

* Graph algorithms
* Knowledge representation
* Information retrieval
* Semantic search
* Reasoning systems
* Rust infrastructure
* Python tooling
* Documentation
* Testing
* Developer experience

Please open an issue before proposing significant architectural changes.

---

# Philosophy

ThinkingOS is built on the belief that the future of personal knowledge management is not about storing more information—it is about improving how we think.

By combining structured knowledge, transparent reasoning, and optional AI assistance, the project aims to provide an open foundation for deeper learning, better research, and more effective decision-making.

---

## License

This project will be released under a permissive open-source license.
