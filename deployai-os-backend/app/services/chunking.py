"""Splits raw document text into retrievable chunks for the knowledge base.

Paragraph-based grouping up to `max_chars`, falling back to word-wrapping
for any single paragraph that's still too long on its own.
"""

import re

_PARAGRAPH_RE = re.compile(r"\n\s*\n")


def chunk_text(text: str, max_chars: int = 600) -> list[str]:
    paragraphs = [p.strip() for p in _PARAGRAPH_RE.split(text) if p.strip()]

    grouped: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) > max_chars and current:
            grouped.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        grouped.append(current)

    final: list[str] = []
    for group in grouped:
        if len(group) <= max_chars:
            final.append(group)
            continue
        words = group.split()
        piece = ""
        for word in words:
            candidate = f"{piece} {word}".strip()
            if len(candidate) > max_chars and piece:
                final.append(piece)
                piece = word
            else:
                piece = candidate
        if piece:
            final.append(piece)

    return final
