"""One check per acceptance criterion in the build specification.

A1 and A12 are the documented commands. The other criteria are exercised here
so a single pytest run shows which of the twelve failed.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.llm import ProviderError, complete
from src.logging_store import CREATE_SQL
from src.pipeline import get_pipeline
from evaluation.harness import run

ROOT = Path(__file__).resolve().parents[1]


def _one_ticket():
    tickets = json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8"))
    return next(ticket for ticket in tickets if ticket["labels"]["intent"] == "api_usage_question")


def test_a2_four_channels_share_one_representation():
    from tests.test_system import test_all_four_channels_normalise

    test_all_four_channels_normalise()


def test_a3_classification_has_intent_urgency_and_confidence():
    result = get_pipeline().process(_one_ticket())
    assert result["intent"]
    assert isinstance(result["urgency"], str) and result["urgency"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["alternatives"]


def test_a4_retrieval_ids_resolve_to_the_corpus():
    from tests.test_system import test_retrieval_returns_a_real_passage

    test_retrieval_returns_a_real_passage()


def test_a5_routing_is_deterministic():
    from tests.test_system import test_same_ticket_routes_the_same_way_twice

    test_same_ticket_routes_the_same_way_twice()


def test_a6_citations_resolve_to_retrieved_passages():
    result = get_pipeline().process(_one_ticket())
    if result["action"] != "sent":
        pytest.skip("this ticket was escalated; citation check needs a sent reply")
    source_ids = {item["passage_id"] for item in result["sources"]}
    assert result["citations"]
    for citation in result["citations"]:
        assert citation["passage_id"] in source_ids


def test_a7_guardrail_blocks_instead_of_sending():
    from tests.test_system import test_prompt_injection_is_blocked

    test_prompt_injection_is_blocked()


def test_a8_decision_log_schema_matches_the_setup_guide():
    for column in (
        "decision_id",
        "created_at",
        "ticket_id",
        "stage",
        "prediction",
        "confidence",
        "threshold",
        "action_taken",
        "reason",
        "sources_used",
        "guardrails",
        "prompt_version",
        "requirement_ids",
    ):
        assert column in CREATE_SQL
    from tests.test_system import test_decision_log_has_one_final_row_per_ticket

    test_decision_log_has_one_final_row_per_ticket()


def test_a9_harness_requires_input_and_output_paths():
    missing = subprocess.run(
        [sys.executable, "-m", "evaluation.harness"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert missing.returncode != 0
    assert "--input" in missing.stderr
    assert "--output" in missing.stderr


def test_a10_metrics_report_contains_the_required_groups(tmp_path):
    sample = json.loads((ROOT / "data" / "validation_tickets.json").read_text(encoding="utf-8"))[:3]
    source = tmp_path / "tickets.json"
    source.write_text(json.dumps(sample), encoding="utf-8")
    report = run(source, tmp_path / "out")
    for group in ("volume", "business", "technical", "governance"):
        assert group in report
    assert {"tickets_processed", "answered_automatically", "escalated", "blocked_by_guardrails"} <= set(
        report["volume"]
    )
    assert "first_contact_resolution_percent" in report["business"]
    assert "classification_per_class" in report["technical"]
    assert "latency_seconds_p95" in report["technical"]
    assert "guardrail_activations_by_type" in report["governance"]
    assert (tmp_path / "out" / "metrics.json").exists()
    assert (tmp_path / "out" / "metrics.md").exists()


def test_a11_timeout_and_rate_limit_do_not_crash(monkeypatch):
    monkeypatch.setenv("USE_LLM", "true")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-not-a-real-key")

    def timeout(system_prompt, user_prompt):
        raise ProviderError("provider timeout")

    monkeypatch.setattr("src.pipeline.complete", timeout)
    result = get_pipeline().process(_one_ticket())
    assert result["action"] in {"sent", "escalated"}
    assert result["model_degraded"] is True

    class Limited:
        status_code = 429

        def json(self):
            return {}

    monkeypatch.setattr("src.llm.time.sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.llm.requests.post", lambda *_args, **_kwargs: Limited())
    with pytest.raises(ProviderError, match="rate limited"):
        complete("system", "user")
