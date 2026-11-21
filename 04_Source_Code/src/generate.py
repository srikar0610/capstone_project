"""Draft an answer by quoting retrieved passages. The ticket is a query, not an instruction.

Requirement FR-GEN-1. Customer text is never concatenated into the draft, so a
ticket cannot redirect the reply. Claims that are not in a retrieved passage
are not added.
"""

from __future__ import annotations

PROMPT_VERSION = "generate-v1"


def _excerpt(passage: str, limit: int = 700) -> str:
    text = " ".join(passage.split())
    marker = text.lower().find("resolution")
    if marker >= 0:
        text = text[marker:]
    if len(text) <= limit:
        return text
    clipped = text[:limit]
    last_space = clipped.rfind(" ")
    if last_space > 200:
        clipped = clipped[:last_space]
    return clipped.rstrip() + "..."


def draft_answer(subject: str, passages: list[dict]) -> dict | None:
    """Return a structured draft, or None when there is nothing safe to say."""
    if not passages:
        return None
    topic = subject.strip() or "your request"
    lines = [
        f"Thanks for contacting CloudServe. Here is what our documentation says about {topic}.",
        "",
    ]
    citations = []
    for passage in passages:
        lines.append(_excerpt(passage["text"]))
        lines.append(f"Source: [{passage['doc_id']}] {passage['title']} ({passage['passage_id']}).")
        lines.append("")
        citations.append(
            {
                "doc_id": passage["doc_id"],
                "passage_id": passage["passage_id"],
                "title": passage["title"],
            }
        )
    lines.append(
        "If this does not clear the problem, reply to this message and a person on the support team will take it from here."
    )
    return {
        "answer": "\n".join(lines).strip(),
        "citations": citations,
        "prompt_version": PROMPT_VERSION,
        "grounded": True,
    }
