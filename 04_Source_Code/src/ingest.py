"""Normalise tickets from all four CloudServe channels into one representation.

Requirement FR-ING-1. Channels in the data are email, chat, docs_comment and forum.
Aliases are accepted so a live chat payload and a community-forum payload do not
need their own downstream code.
"""

from __future__ import annotations

import uuid
from typing import Any

CHANNEL_ALIASES = {
    "email": "email",
    "e-mail": "email",
    "mail": "email",
    "chat": "chat",
    "live_chat": "chat",
    "live chat": "chat",
    "livechat": "chat",
    "docs_comment": "docs_comment",
    "doc_comment": "docs_comment",
    "documentation": "docs_comment",
    "documentation_comment": "docs_comment",
    "documentation comment": "docs_comment",
    "docs": "docs_comment",
    "forum": "forum",
    "community": "forum",
    "community_forum": "forum",
    "community forum": "forum",
}

CANONICAL_CHANNELS = ("email", "chat", "docs_comment", "forum")


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def normalise(raw: Any) -> dict[str, Any]:
    """Return one internal ticket. Malformed input becomes an empty ticket instead of an exception."""
    malformed_input = not isinstance(raw, dict)
    if malformed_input:
        raw = {}
    original_channel = _text(raw.get("channel")).strip()
    channel = CHANNEL_ALIASES.get(original_channel.lower(), original_channel.lower() or "unknown")
    ticket_id = _text(raw.get("ticket_id")).strip() or f"MALFORMED-{uuid.uuid4().hex[:8]}"
    subject = _text(raw.get("subject"))
    body = _text(raw.get("body"))
    return {
        "ticket_id": ticket_id,
        "channel": channel,
        "raw_channel": original_channel,
        "subject": subject,
        "body": body,
        "original_text": f"{subject}\n{body}".strip(),
        "received_at": _text(raw.get("received_at")),
        "customer_id": _text(raw.get("customer_id")),
        "customer_tier": _text(raw.get("customer_tier")) or "unknown",
        "customer_region": _text(raw.get("customer_region")) or "unknown",
        "language_fluency": _text(raw.get("language_fluency")) or "unknown",
        "labels": raw.get("labels") if isinstance(raw.get("labels"), dict) else {},
        "malformed": malformed_input or (not subject.strip() and not body.strip()),
        "known_channel": channel in CANONICAL_CHANNELS,
    }
