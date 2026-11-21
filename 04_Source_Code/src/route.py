"""Decide whether to send an answer or hand the ticket to a person.

Requirement FR-RTE-1. The same classification, sources and guardrail result
always produce the same decision. Four intents are never answered automatically,
because every development ticket with those intents was marked must-not-auto.
"""

from __future__ import annotations

PROMPT_VERSION = "route-v1"

# High-urgency cases of these two intents were passed to a person on the
# development tickets even when a document existed. High-urgency deployment
# failures were usually answered from the docs, so they are not in this set.
ESCALATE_WHEN_HIGH = {
    "database_issue": "High-urgency database failures are escalated. A document may explain the symptom, but the development history shows a person still took these.",
    "performance_degradation": "High-urgency performance problems are escalated so an engineer sees them, with the retrieved article attached.",
}


# Every development ticket with these intents has must_not_auto_respond = true.
NEVER_AUTO = {
    "security_incident": "Security incidents are handled by a person. An automatic reply could hide an active compromise.",
    "compliance_request": "Compliance and audit requests need a person who can confirm what may be released.",
    "feature_request": "Feature requests are product decisions. Documentation cannot close them.",
    "unclear_request": "The request is not clear enough to answer from the documentation.",
}


def decide(
    *,
    intent: str,
    urgency: str,
    confidence: float,
    sources: list[dict],
    guardrail_blocked: bool,
    guardrail_reason: str,
    confidence_threshold: float,
    kill_switch: bool,
) -> dict:
    threshold = confidence_threshold
    if kill_switch:
        return _decision(
            "escalated",
            "The kill switch is on, so every ticket is handed to a person.",
            threshold,
            False,
        )
    if guardrail_blocked:
        return _decision("escalated", guardrail_reason, threshold, True)
    if intent in NEVER_AUTO:
        return _decision("escalated", NEVER_AUTO[intent], threshold, False)
    if urgency == "high" and intent in ESCALATE_WHEN_HIGH:
        return _decision("escalated", ESCALATE_WHEN_HIGH[intent], threshold, False)
    if confidence < threshold:
        return _decision(
            "escalated",
            (
                f"Intent confidence is {confidence:.2f}, below the threshold of {threshold:.2f}. "
                "A person should confirm the request before a customer sees an answer."
            ),
            threshold,
            False,
        )
    if not sources:
        return _decision(
            "escalated",
            "No documentation passage scored above the relevance threshold, so there is nothing safe to send.",
            threshold,
            False,
        )
    cited = ", ".join(source["doc_id"] for source in sources)
    return _decision(
        "sent",
        (
            f"Classified as {intent} with confidence {confidence:.2f}, "
            f"which is at or above {threshold:.2f}, and supported by {cited}."
        ),
        threshold,
        False,
    )


def _decision(action: str, reason: str, threshold: float, blocked: bool) -> dict:
    return {
        "action": action,
        "reason": reason,
        "threshold": threshold,
        "blocked_by_guardrail": blocked,
        "prompt_version": PROMPT_VERSION,
    }
