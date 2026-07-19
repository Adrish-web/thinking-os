# ThinkingOS

> **An open-source operating system for thinking.**
>
> ThinkingOS is a local-first knowledge and reasoning engine designed to help researchers, students, engineers, and lifelong learners build, connect, and reason over knowledge—not just store notes.

---

## Vision

Most knowledge management tools optimize for **collecting information**.

ThinkingOS is designed to optimize for **thinking**.

Instead of asking:

> *"Where did I save this note?"*

ThinkingOS helps answer:

* What do I already know?
* How are these ideas connected?
* What evidence supports this claim?
* Where are the contradictions?
* What am I missing?
* What should I learn next?

The long-term goal is to build a personal reasoning system that grows with its user.

---

# Core Principles

### 🧠 Thinking First

Knowledge is valuable only when it improves reasoning.

ThinkingOS is built around planning, synthesis, evidence, and understanding—not note storage alone.

---

### 🌐 Local First

Your knowledge belongs to you.

The entire core system works offline.

No account.

No subscription.

No mandatory cloud services.

---

### 🔌 AI Optional

Large language models are plugins—not dependencies.

ThinkingOS should remain useful without any external AI.

Supported providers may include:

* Local models (Ollama)
* Anthropic Claude
* OpenAI
* Gemini
* Future providers

The reasoning engine never depends on a specific model.

---

### 📖 Open Source

ThinkingOS is built in the open.

The architecture is intended to be transparent, extensible, and community-driven.

---

# Architecture

```text
                ThinkingOS

                     │
        ┌────────────┴────────────┐
        │                         │
   Knowledge Engine          AI Providers
        │                         │
        │                  Claude / GPT
        │                  Gemini
        │                  Ollama
        │
 ┌─────────────────────────────────────┐
 │ Parser                              │
 │ Knowledge Graph                     │
 │ Ontology                            │
 │ Search                              │
 │ Event Store                         │
 │ Planner                             │
 │ Reasoning Engine                    │
 └─────────────────────────────────────┘
```

---

# Repository Structure

```text
thinking-os/

├── crates/             # Rust core libraries
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

# Current Features

* Markdown parsing
* Knowledge graph construction
* Graph search
* Event-sourced history
* Local reasoning pipeline
* Pluggable AI provider interface
* Python prototype
* Rust core libraries

---

# Roadmap

## Phase 1 — Knowledge Engine

* Markdown parser
* Graph construction
* Search
* Event sourcing
* CLI

## Phase 2 — Semantic Knowledge

* Typed ontology
* Claims
* Evidence
* Papers
* Questions
* Experiments

## Phase 3 — Reasoning

* Multi-step planning
* Evidence retrieval
* Hypothesis generation
* Contradiction detection
* Knowledge synthesis

## Phase 4 — Research Workspace

* Interactive graph
* Obsidian integration
* VS Code extension
* Web interface

## Phase 5 — Thinking OS

A system that continuously helps users:

* organize knowledge
* understand ideas
* discover connections
* identify gaps
* develop better reasoning

---

# Design Philosophy

ThinkingOS separates **knowledge representation** from **intelligence**.

The knowledge graph is the source of truth.

Reasoning is reproducible.

AI enhances the process but does not replace it.

This allows the system to remain useful regardless of which language models are available in the future.

---

# Why Rust + Python?

**Rust**

* High-performance graph engine
* Storage
* Search
* Query execution
* Long-term production runtime

**Python**

* Rapid prototyping
* AI orchestration
* Research workflows
* Experimentation
* Notebook integration

The public APIs are designed so that Python can orchestrate the system while the performance-critical components live in Rust.

---

# Contributing

ThinkingOS is still in its early stages.

Contributions are welcome in areas including:

* Graph algorithms
* Information retrieval
* Knowledge representation
* Scientific workflows
* Local AI integration
* Developer tooling
* Documentation
* Testing

Please open an issue before implementing major architectural changes.

---

# Long-Term Goal

Build an open, local-first, extensible platform that helps people think more clearly—not just collect more information.

If successful, ThinkingOS should become a foundation for research, learning, writing, and scientific discovery that remains accessible to everyone, with optional AI enhancements rather than mandatory cloud dependencies.

---

## License

This project will be released under a permissive open-source license (to be decided).
