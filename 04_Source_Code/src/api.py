"""HTTP interface. Start with: python -m src.api"""

from __future__ import annotations

from typing import Any

import uvicorn
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from pydantic import BaseModel, ConfigDict

from src.config import get_settings
from src.logging_config import configure_logging
from src.pipeline import process_ticket

app = FastAPI(
    title="CloudServe support system",
    summary="Answers tickets from CloudServe documentation and escalates everything else.",
    version="1.0.0",
)
app.mount("/metrics", make_asgi_app())


class TicketPayload(BaseModel):
    """Extra fields from the source channel are preserved and ignored by the model."""

    model_config = ConfigDict(extra="allow")

    ticket_id: str | None = None
    channel: str | None = None
    subject: str | None = None
    body: str | None = None
    received_at: str | None = None
    customer_id: str | None = None
    customer_tier: str | None = None
    customer_region: str | None = None
    language_fluency: str | None = None


@app.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "use_llm": settings.use_llm,
        "kill_switch": settings.kill_switch,
        "confidence_threshold": settings.confidence_threshold,
        "relevance_threshold": settings.relevance_threshold,
    }


@app.post("/tickets")
def submit_ticket(payload: TicketPayload) -> dict[str, Any]:
    result = process_ticket(payload.model_dump())
    result.pop("labels", None)
    return result


def main() -> None:
    configure_logging()
    # Build the index once, before the server accepts traffic.
    from src.pipeline import get_pipeline

    get_pipeline()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
