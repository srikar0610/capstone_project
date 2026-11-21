"""Persistent decision log. One final row per ticket is what the harness reconciles.

Requirement FR-LOG-1. The columns match the minimum schema in the setup guide.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS decisions (
    decision_id     TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL,
    ticket_id       TEXT NOT NULL,
    stage           TEXT NOT NULL,
    prediction      TEXT,
    confidence      REAL,
    threshold       REAL,
    action_taken    TEXT NOT NULL,
    reason          TEXT NOT NULL,
    sources_used    TEXT,
    guardrails      TEXT,
    prompt_version  TEXT,
    requirement_ids TEXT
)
"""


class DecisionLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{path.resolve().as_posix()}", future=True)
        self._lock = threading.Lock()
        with self.engine.begin() as connection:
            connection.execute(text(CREATE_SQL))

    def write(
        self,
        *,
        ticket_id: str,
        stage: str,
        action_taken: str,
        reason: str,
        prediction: dict | None = None,
        confidence: float | None = None,
        threshold: float | None = None,
        sources: list | None = None,
        guardrails: list | None = None,
        prompt_version: str = "",
        requirement_ids: str = "",
    ) -> str:
        decision_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        statement = text(
            """
            INSERT INTO decisions (
                decision_id, created_at, ticket_id, stage, prediction, confidence,
                threshold, action_taken, reason, sources_used, guardrails,
                prompt_version, requirement_ids
            ) VALUES (
                :decision_id, :created_at, :ticket_id, :stage, :prediction, :confidence,
                :threshold, :action_taken, :reason, :sources_used, :guardrails,
                :prompt_version, :requirement_ids
            )
            """
        )
        payload = {
            "decision_id": decision_id,
            "created_at": created_at,
            "ticket_id": ticket_id,
            "stage": stage,
            "prediction": json.dumps(prediction) if prediction is not None else None,
            "confidence": confidence,
            "threshold": threshold,
            "action_taken": action_taken,
            "reason": reason,
            "sources_used": json.dumps(sources or []),
            "guardrails": json.dumps(guardrails or []),
            "prompt_version": prompt_version,
            "requirement_ids": requirement_ids,
        }
        with self._lock, self.engine.begin() as connection:
            connection.execute(statement, payload)
        return decision_id

    def count_final(self, ticket_ids: list[str], started_at: str | None = None) -> int:
        if not ticket_ids:
            return 0
        # SQLite variable limits sit well above the hidden set of 120.
        placeholders = ", ".join(f":id{i}" for i in range(len(ticket_ids)))
        params: dict = {f"id{i}": ticket_id for i, ticket_id in enumerate(ticket_ids)}
        started_clause = ""
        if started_at:
            started_clause = " AND created_at >= :started_at"
            params["started_at"] = started_at
        statement = text(
            f"""
            SELECT COUNT(*) AS n FROM decisions
            WHERE stage = 'final' AND ticket_id IN ({placeholders}){started_clause}
            """
        )
        with self.engine.connect() as connection:
            row = connection.execute(statement, params).one()
        return int(row.n)
