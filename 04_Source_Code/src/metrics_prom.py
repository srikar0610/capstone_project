"""Prometheus counters. The API exposes them; the harness still writes a file report."""

from prometheus_client import Counter, Histogram

TICKETS = Counter(
    "tickets_processed_total",
    "Tickets processed",
    ["channel", "outcome"],
)
GUARDRAIL = Counter(
    "guardrail_blocks_total",
    "Responses blocked by a guardrail",
    ["guardrail"],
)
LATENCY = Histogram(
    "response_seconds",
    "End to end processing time",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 10),
)
