"""
AI Support Agent — Tier 0.
Combines RAG retrieval with Claude Opus 4.6 to answer OMS support questions.
Streams responses and tracks confidence for escalation decisions.
"""
import json
from typing import AsyncIterator

import anthropic

from config import settings
from knowledge.vector_store import search

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


AGENT_SYSTEM = """You are an expert AI support agent for Open Money Stack (OMS) by Polygon.
OMS is a modular, open-source financial infrastructure stack that enables builders to create
payment rails, wallets, and DeFi products on Polygon's network.

Your role:
- Answer support questions accurately using the provided documentation context
- Be helpful and concise — developers and enterprise teams value precision
- If you're not confident in an answer, say so clearly and offer to connect them with a human expert
- For security concerns, always escalate immediately
- Tailor your tone to the audience: technical for developers, business-focused for enterprise partners

When answering:
1. Use the retrieved documentation context when available
2. Cite the source document when referencing specific information
3. Provide code examples for integration questions when helpful
4. If the question is outside your knowledge, say: "I don't have enough information to answer this confidently. Let me connect you with our support team."

IMPORTANT: After your answer, output a JSON block on a new line in exactly this format:
<confidence>{"score": 0.85, "needs_human": false, "reason": null}</confidence>
Score 0.0–1.0. Set needs_human=true if the question requires human expertise."""


def _build_rag_context(query: str, n_results: int = 5) -> tuple[str, list[str]]:
    results = search(query, n_results=n_results)
    if not results:
        return "", []

    context_parts = []
    doc_ids = []
    for r in results:
        if r["score"] < 0.3:  # skip low-relevance results
            continue
        meta = r["metadata"]
        context_parts.append(
            f"[Source: {meta.get('title', meta.get('source', 'OMS Docs'))}]\n{r['text']}"
        )
        doc_ids.append(r["id"])

    return "\n\n---\n\n".join(context_parts), doc_ids


def _build_messages(
    history: list[dict],
    user_message: str,
    rag_context: str,
) -> list[dict]:
    messages = []

    # Inject history
    for msg in history[-10:]:  # keep last 10 turns
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Build user message with RAG context
    if rag_context:
        content = (
            f"<documentation>\n{rag_context}\n</documentation>\n\n"
            f"User question: {user_message}"
        )
    else:
        content = user_message

    messages.append({"role": "user", "content": content})
    return messages


async def stream_response(
    user_message: str,
    history: list[dict],
    audience: str = "unknown",
) -> AsyncIterator[dict]:
    """
    Yields dicts:
      {"type": "text", "text": "..."}        — streaming text delta
      {"type": "done", "confidence": {...}, "doc_ids": [...]}  — final metadata
    """
    rag_context, doc_ids = _build_rag_context(user_message)

    audience_note = {
        "developer": "The user is a developer integrating OMS.",
        "enterprise": "The user is an enterprise partner. Be professional and thorough.",
        "end_user": "The user is an end user of a product built on OMS. Use simple language.",
    }.get(audience, "")

    system = AGENT_SYSTEM
    if audience_note:
        system += f"\n\nAudience context: {audience_note}"

    messages = _build_messages(history, user_message, rag_context)

    full_text = ""
    async with get_client().messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=system,
        messages=messages,
    ) as stream:
        async for event in stream:
            if (
                event.type == "content_block_delta"
                and hasattr(event.delta, "type")
                and event.delta.type == "text_delta"
            ):
                text = event.delta.text
                full_text += text
                yield {"type": "text", "text": text}

    # Parse confidence block from response
    confidence = {"score": 0.5, "needs_human": False, "reason": None}
    if "<confidence>" in full_text and "</confidence>" in full_text:
        try:
            raw = full_text.split("<confidence>")[1].split("</confidence>")[0].strip()
            confidence = json.loads(raw)
        except (json.JSONDecodeError, IndexError):
            pass

    yield {"type": "done", "confidence": confidence, "doc_ids": doc_ids}


async def get_response(
    user_message: str,
    history: list[dict],
    audience: str = "unknown",
) -> tuple[str, dict, list[str]]:
    """Non-streaming version. Returns (text, confidence, doc_ids)."""
    full_text = ""
    confidence = {}
    doc_ids = []

    async for chunk in stream_response(user_message, history, audience):
        if chunk["type"] == "text":
            full_text += chunk["text"]
        elif chunk["type"] == "done":
            confidence = chunk["confidence"]
            doc_ids = chunk["doc_ids"]

    # Strip the confidence JSON from the displayed text
    if "<confidence>" in full_text:
        full_text = full_text.split("<confidence>")[0].strip()

    return full_text, confidence, doc_ids
