"""Prompt templates.

All strings the pipeline sends to an LLM live here, so behaviour tuning never
touches pipeline code and the Rust port can lift the templates verbatim.
"""

from __future__ import annotations

from .reasoning import ReasoningContext

SYSTEM_PROMPT = (
    "You are ThinkingOS, an AI reasoning agent. Answer the user's question "
    "STRICTLY using the provided context graph. Do not hallucinate external "
    "knowledge. If the context graph is empty or irrelevant, say so and give "
    "a brief best-effort answer clearly marked as outside the vault."
)

ADVERSARY_SYSTEM_PROMPT = (
    "You are the ThinkingOS adversary. Your job is to attack a draft answer: "
    "find unsupported claims, contradictions with the context graph, and "
    "logical gaps. Be terse and specific. If the draft holds up, reply "
    "exactly: OK."
)


def render_context(context: ReasoningContext) -> str:
    """Serialize retrieved context as the XML block the Rust engine emits."""
    lines = ["<context_graph>"]
    lines.append("  <entry_nodes>")
    for node, _score in context.entry_nodes:
        flat = " ".join(node.content.split())
        lines.append(f"    <node>{flat}</node>")
    lines.append("  </entry_nodes>")
    lines.append("  <semantic_neighborhood>")
    for node in context.neighborhood:
        lines.append(f"    <concept>{node.content}</concept>")
    lines.append("  </semantic_neighborhood>")
    lines.append("</context_graph>")
    return "\n".join(lines)


def render_ask_prompt(question: str, context: ReasoningContext) -> str:
    if context.is_empty():
        context_block = "<context_graph/> (vault empty or no relevant notes)"
    else:
        context_block = render_context(context)
    return f"{context_block}\n\nUser Question: {question}"


def render_adversary_prompt(question: str, draft: str, context: ReasoningContext) -> str:
    return (
        f"{render_ask_prompt(question, context)}\n\n"
        f"Draft answer under review:\n{draft}"
    )


def render_revision_prompt(
    question: str, draft: str, critique: str, context: ReasoningContext
) -> str:
    return (
        f"{render_ask_prompt(question, context)}\n\n"
        f"Your previous draft:\n{draft}\n\n"
        f"An adversarial reviewer raised these objections:\n{critique}\n\n"
        "Revise the draft to address every valid objection. Keep what was correct."
    )
