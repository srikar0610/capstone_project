"""Metrics the harness writes without any manual calculation.

Figures follow the evaluation framework: volume, business outcomes, technical
performance and governance. Classification scores are computed only when the
input file carries labels. A file without labels still produces the operational
figures.
"""

from __future__ import annotations

import statistics
from collections import defaultdict

from sklearn.metrics import precision_recall_fscore_support


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(100.0 * numerator / denominator, 2)


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(fraction * (len(ordered) - 1)))))
    return round(ordered[index], 4)


def build_report(results: list[dict]) -> dict:
    total = len(results)
    sent = [item for item in results if item["action"] == "sent" and not item["blocked_by_guardrail"]]
    escalated = [item for item in results if item["action"] == "escalated" or item["blocked_by_guardrail"]]
    blocked = [item for item in results if item["blocked_by_guardrail"]]
    latencies = [float(item["latency_seconds"]) for item in results]
    labelled = [item for item in results if item.get("labels", {}).get("intent")]

    per_class: dict = {}
    macro_precision = None
    if labelled:
        y_true = [item["labels"]["intent"] for item in labelled]
        y_pred = [item["intent"] for item in labelled]
        labels = sorted(set(y_true) | set(y_pred))
        precision, recall, fscore, support = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, zero_division=0
        )
        for index, label in enumerate(labels):
            per_class[label] = {
                "precision": round(float(precision[index]), 4),
                "recall": round(float(recall[index]), 4),
                "f1": round(float(fscore[index]), 4),
                "support": int(support[index]),
            }
        macro_precision = round(float(sum(precision) / len(precision)), 4) if labels else None

    retrieval_hits = 0
    retrieval_expected = 0
    expected_known = 0
    citation_ok = 0
    citation_total = 0
    for item in results:
        if item["sources"]:
            retrieval_hits += 1
        expected_docs = (item.get("labels") or {}).get("expected_doc_ids") or []
        if expected_docs:
            expected_known += 1
            found = {source["doc_id"] for source in item["sources"]}
            if found & set(expected_docs):
                retrieval_expected += 1
        for citation in item.get("citations") or []:
            citation_total += 1
            source_ids = {source["doc_id"] for source in item["sources"]}
            passage_ids = {source["passage_id"] for source in item["sources"]}
            if citation["doc_id"] in source_ids and citation["passage_id"] in passage_ids:
                citation_ok += 1

    guardrail_counts: dict[str, int] = defaultdict(int)
    private_data_blocks = 0
    for item in results:
        for check in item.get("guardrails") or []:
            if check.get("blocked"):
                guardrail_counts[check["name"]] += 1
                if check["name"] == "private_data":
                    private_data_blocks += 1

    def group_gap(field: str) -> dict:
        buckets: dict[str, list[bool]] = defaultdict(list)
        for item in results:
            answered = item["action"] == "sent" and not item["blocked_by_guardrail"]
            buckets[str(item.get(field) or "unknown")].append(answered)
        rates = {
            name: round(100.0 * sum(flags) / len(flags), 2)
            for name, flags in buckets.items()
            if flags
        }
        if len(rates) < 2:
            return {"rates": rates, "max_gap_percentage_points": 0.0}
        values = list(rates.values())
        return {
            "rates": rates,
            "max_gap_percentage_points": round(max(values) - min(values), 2),
        }

    confidence_bins = []
    if labelled:
        for start in range(0, 10):
            low, high = start / 10, (start + 1) / 10
            group = [
                item
                for item in labelled
                if low <= float(item["confidence"]) < high or (high == 1 and float(item["confidence"]) == 1)
            ]
            if not group:
                continue
            stated = sum(float(item["confidence"]) for item in group) / len(group)
            observed = sum(1 for item in group if item["intent"] == item["labels"]["intent"]) / len(group)
            confidence_bins.append(
                {
                    "low": low,
                    "high": high,
                    "count": len(group),
                    "stated_confidence": round(stated, 4),
                    "observed_accuracy": round(observed, 4),
                    "gap": round(stated - observed, 4),
                }
            )

    mean_seconds = statistics.mean(latencies) if latencies else None
    median_seconds = statistics.median(latencies) if latencies else None
    return {
        "volume": {
            "tickets_processed": total,
            "answered_automatically": len(sent),
            "escalated": len(escalated),
            "blocked_by_guardrails": len(blocked),
        },
        "business": {
            "first_contact_resolution_percent": _rate(len(sent), total),
            "escalation_rate_percent": _rate(len(escalated), total),
            "mean_response_minutes": round(mean_seconds / 60, 4) if mean_seconds is not None else None,
            "median_response_minutes": round(median_seconds / 60, 4) if median_seconds is not None else None,
            "baseline_first_contact_resolution_percent": 42,
            "target_first_contact_resolution_percent": 60,
            "baseline_reply_hours": "8-12",
            "target_reply_minutes": 5,
            "notes": (
                "First contact resolution counts tickets answered from documentation "
                "without a person. Response time is processing time, because an "
                "automatic reply is sent as soon as the decision is logged. "
                "Customer satisfaction is not estimated here; it needs a human review sample."
            ),
        },
        "technical": {
            "tickets_with_labels": len(labelled),
            "classification_macro_precision": macro_precision,
            "classification_per_class": per_class,
            "retrieval_passage_rate_percent": _rate(retrieval_hits, total),
            "retrieval_expected_doc_hit_percent": _rate(retrieval_expected, expected_known),
            "citation_accuracy_percent": _rate(citation_ok, citation_total) if citation_total else None,
            "latency_seconds_median": _percentile(latencies, 0.50),
            "latency_seconds_p95": _percentile(latencies, 0.95),
            "model_degraded_tickets": sum(1 for item in results if item.get("model_degraded")),
        },
        "governance": {
            "decisions_logged": total,
            "guardrail_activations_by_type": dict(guardrail_counts),
            "private_data_detections": private_data_blocks,
            "fairness_auto_answer_rate": {
                "customer_tier": group_gap("customer_tier"),
                "customer_region": group_gap("customer_region"),
                "language_fluency": group_gap("language_fluency"),
            },
            "confidence_calibration": confidence_bins,
        },
    }


def render_markdown(report: dict) -> str:
    volume = report["volume"]
    business = report["business"]
    technical = report["technical"]
    governance = report["governance"]
    lines = [
        "# Evaluation report",
        "",
        "## Volume",
        f"- Tickets processed: {volume['tickets_processed']}",
        f"- Answered automatically: {volume['answered_automatically']}",
        f"- Escalated: {volume['escalated']}",
        f"- Blocked by guardrails: {volume['blocked_by_guardrails']}",
        "",
        "## Business",
        f"- First contact resolution: {business['first_contact_resolution_percent']}% "
        f"(baseline {business['baseline_first_contact_resolution_percent']}%, "
        f"target {business['target_first_contact_resolution_percent']}%)",
        f"- Escalation rate: {business['escalation_rate_percent']}%",
        f"- Mean response time: {business['mean_response_minutes']} minutes",
        f"- Median response time: {business['median_response_minutes']} minutes",
        f"- {business['notes']}",
        "",
        "## Technical",
        f"- Classification macro precision: {technical['classification_macro_precision']}",
        f"- Retrieval returned a passage: {technical['retrieval_passage_rate_percent']}%",
        f"- Retrieval hit an expected document: {technical['retrieval_expected_doc_hit_percent']}%",
        f"- Citation accuracy: {technical['citation_accuracy_percent']}%",
        f"- Latency median seconds: {technical['latency_seconds_median']}",
        f"- Latency 95th percentile seconds: {technical['latency_seconds_p95']}",
        "",
        "## Governance",
        f"- Decisions logged: {governance['decisions_logged']}",
        f"- Private data detections: {governance['private_data_detections']}",
        f"- Guardrail activations: {governance['guardrail_activations_by_type']}",
        "",
        "These figures should be treated with caution because automatic resolution "
        "counts a cited documentation reply as first contact resolution, and "
        "satisfaction has not been scored by a person.",
        "",
    ]
    return "\n".join(lines)
