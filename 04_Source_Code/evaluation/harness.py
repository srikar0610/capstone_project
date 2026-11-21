"""Process every ticket in a file and write a metrics report.

Usage, from the project root:

    python -m evaluation.harness --input data/validation_tickets.json --output evaluation/results
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.logging_config import configure_logging
from src.pipeline import get_pipeline


def load_tickets(path: Path) -> list:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("tickets", "data", "items"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError(f"{path} must be a JSON list of tickets, or an object with a tickets list.")


def failure_result(raw: object, exc: BaseException) -> dict:
    ticket_id = "MALFORMED"
    if isinstance(raw, dict) and raw.get("ticket_id"):
        ticket_id = str(raw["ticket_id"])
    return {
        "ticket_id": ticket_id,
        "channel": "unknown",
        "known_channel": False,
        "customer_tier": "unknown",
        "customer_region": "unknown",
        "language_fluency": "unknown",
        "intent": "unclear_request",
        "urgency": "low",
        "confidence": 0.0,
        "alternatives": [],
        "sources": [],
        "action": "escalated",
        "blocked_by_guardrail": False,
        "reason": f"The ticket could not be processed and was escalated: {exc}",
        "customer_message": (
            "Thank you for contacting CloudServe. A person on the support team will take this from here."
        ),
        "citations": [],
        "guardrails": [],
        "escalation_summary": f"Processing error: {exc}",
        "model_degraded": False,
        "degradation_reason": "",
        "latency_seconds": 0.0,
        "prompt_versions": {},
        "labels": raw.get("labels") if isinstance(raw, dict) and isinstance(raw.get("labels"), dict) else {},
        "error": "".join(traceback.format_exception_only(type(exc), exc)).strip(),
    }


def run(input_path: Path, output_dir: Path) -> dict:
    from evaluation.report import build_report, render_markdown

    configure_logging()
    started_at = datetime.now(timezone.utc).isoformat()
    tickets = load_tickets(input_path)
    pipeline = get_pipeline()
    results = []
    for index, ticket in enumerate(tickets, start=1):
        try:
            results.append(pipeline.process(ticket))
        except Exception as exc:  # noqa: BLE001 - one bad ticket must not stop the run
            results.append(failure_result(ticket, exc))
        if index % 20 == 0 or index == len(tickets):
            print(f"processed {index}/{len(tickets)}", file=sys.stderr)
    report = build_report(results)
    if input_path.stem == "development_tickets":
        report["technical"]["training_set_warning"] = (
            "This file is the classifier's training data. "
            "Precision on it is not an evaluation result. "
            "Point --input at a file the model was not trained on."
        )
    logged = pipeline.log.count_final([item["ticket_id"] for item in results], started_at=started_at)
    report["governance"]["decisions_logged"] = logged
    report["governance"]["decisions_match_tickets"] = logged == len(results)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "tickets.jsonl").write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in results) + "\n",
        encoding="utf-8",
    )
    (output_dir / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_dir / "metrics.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the support system over a ticket file.")
    parser.add_argument("--input", required=True, help="Path to a JSON ticket file.")
    parser.add_argument("--output", required=True, help="Directory for the metrics report and per-ticket results.")
    args = parser.parse_args()
    report = run(Path(args.input), Path(args.output))
    volume = report["volume"]
    print(
        f"finished tickets={volume['tickets_processed']} "
        f"sent={volume['answered_automatically']} "
        f"escalated={volume['escalated']} "
        f"blocked={volume['blocked_by_guardrails']}"
    )


if __name__ == "__main__":
    main()
