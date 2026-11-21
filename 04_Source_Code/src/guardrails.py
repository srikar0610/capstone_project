"""Checks that can stop a reply. A warning that still sends the text is not a guardrail.

Requirement FR-GRD-1. Three checks run on every draft: prompt injection in the
ticket, private data in the outbound text, and claims the sources do not support.
"""

from __future__ import annotations

import re

PROMPT_VERSION = "guardrails-v1"

INJECTION_PATTERNS = (
    r"ignore (all |any )?(previous|prior|above) (instructions|rules|prompts)",
    r"disregard (your|the) (instructions|rules|prompt|guidelines)",
    r"reveal (your )?(system )?prompt",
    r"you are now",
    r"jailbreak",
    r"do not follow (your|the) (policy|rules|instructions)",
)

PRIVATE_DATA_PATTERNS = (
    ("email_address", r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE),
    ("payment_card", r"\b(?:\d[ \-]?){13,19}\b", 0),
    ("secret_key", r"\b(?:sk_live_|sk-|AKIA)[A-Za-z0-9_\-]{8,}", 0),
    ("private_key_block", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", 0),
)

# Phrases senior agents marked as claims a reply must not invent.
UNSUPPORTED_CLAIMS = (
    "a refund has been issued",
    "refund has been issued",
    "the issue has been fixed on our side",
    "has been fixed on our side",
    "we have fixed this",
    "a specific delivery date",
    "will be delivered on",
    "the fix will ship on",
)


def _hit(name: str, blocked: bool, detail: str) -> dict:
    return {
        "name": name,
        "blocked": blocked,
        "detail": detail,
        "prompt_version": PROMPT_VERSION,
    }


def check_injection(ticket_text: str) -> dict:
    text = ticket_text or ""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return _hit(
                "prompt_injection",
                True,
                "The ticket tries to override the system instructions, so no automatic reply is sent.",
            )
    return _hit("prompt_injection", False, "No instruction override detected.")


def check_private_data(outbound: str) -> dict:
    text = outbound or ""
    for name, pattern, flags in PRIVATE_DATA_PATTERNS:
        if re.search(pattern, text, flags=flags):
            return _hit(
                "private_data",
                True,
                f"Outbound text matched the {name} check and was not sent.",
            )
    return _hit("private_data", False, "No private data pattern in the outbound text.")


def check_unsupported_claims(outbound: str, passages: list[dict]) -> dict:
    text = (outbound or "").lower()
    source = "\n".join(passage.get("text", "") for passage in passages).lower()
    for claim in UNSUPPORTED_CLAIMS:
        if claim in text and claim not in source:
            return _hit(
                "unsupported_claim",
                True,
                f"The draft contains '{claim}', which is not in the retrieved passages.",
            )
    return _hit("unsupported_claim", False, "No prohibited claim outside the sources.")


def review(ticket_text: str, outbound: str, passages: list[dict]) -> dict:
    """Run every check. Any block prevents the reply from being sent."""
    checks = [
        check_injection(ticket_text),
        check_private_data(outbound),
        check_unsupported_claims(outbound, passages),
    ]
    blocked = [item for item in checks if item["blocked"]]
    return {
        "blocked": bool(blocked),
        "checks": checks,
        "reason": blocked[0]["detail"] if blocked else "All guardrails passed.",
        "prompt_version": PROMPT_VERSION,
    }
