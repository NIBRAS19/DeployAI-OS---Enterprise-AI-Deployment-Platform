"""Assistant reply generation: a real call to Claude when an API key is
configured, and a deterministic offline fallback when it isn't — so the
/assistants/chat endpoint always works with zero external setup, and
upgrades to real, cited answers the moment a key is added to .env.
"""

import httpx

from app.config import get_settings
from app.services.rag import RetrievalOutcome

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-6"


def _mock_reply(outcome: RetrievalOutcome) -> str:
    if not outcome.chunks:
        return (
            "I couldn't find anything in the knowledge base that answers that — "
            "you may want to check with the relevant team directly."
        )
    top = outcome.chunks[0].chunk
    source = top.document.filename if top.document else "the knowledge base"
    return f"Based on {source}: {top.content}"


def _build_system_prompt(outcome: RetrievalOutcome) -> str:
    context = "\n\n".join(
        f"[{i + 1}] ({scored.chunk.document.filename if scored.chunk.document else 'source'}) "
        f"{scored.chunk.content}"
        for i, scored in enumerate(outcome.chunks)
    )
    return (
        "You are an internal company knowledge assistant. Answer ONLY using the "
        "numbered context passages below, and cite the passage number(s) you used "
        "(e.g. \"[1]\"). If the passages don't contain the answer, say you don't "
        "know rather than guessing.\n\nContext:\n" + context
    )


def generate_reply(question: str, outcome: RetrievalOutcome) -> tuple[str, str]:
    """Returns (reply_text, generated_by), generated_by being "claude" or
    "mock". Restricted outcomes never reach the model at all — the refusal
    message is returned as-is.
    """
    if outcome.restricted:
        return outcome.message or "I'm not able to help with that.", "mock"

    settings = get_settings()
    if not settings.anthropic_api_key:
        return _mock_reply(outcome), "mock"

    try:
        response = httpx.post(
            ANTHROPIC_MESSAGES_URL,
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
            json={
                "model": DEFAULT_MODEL,
                "max_tokens": 500,
                "system": _build_system_prompt(outcome),
                "messages": [{"role": "user", "content": question}],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        data = response.json()
        text_blocks = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
        reply = "\n".join(text_blocks).strip()
        return (reply or _mock_reply(outcome)), "claude"
    except httpx.HTTPError:
        return _mock_reply(outcome), "mock"
