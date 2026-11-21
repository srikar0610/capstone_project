"""Runtime configuration. Values come from the environment, then .env, then defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


@dataclass(frozen=True)
class Settings:
    root: Path
    use_llm: bool
    api_key: str
    model_name: str
    database_path: Path
    log_level: str
    confidence_threshold: float
    retrieval_top_k: int
    relevance_threshold: float
    kill_switch: bool
    prometheus_port: int
    development_tickets: Path
    documentation: Path


def database_path() -> Path:
    """Resolve DATABASE_URL to a filesystem path. Relative paths sit under the project root."""
    url = os.getenv("DATABASE_URL", "sqlite:///./storage/decisions.db")
    if not url.startswith("sqlite:///"):
        raise ValueError("This build records decisions in SQLite. DATABASE_URL must start with sqlite:///")
    raw = url[len("sqlite:///") :]
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_settings() -> Settings:
    """Read configuration at call time so tests and the harness can override it."""
    return Settings(
        root=ROOT,
        use_llm=_flag("USE_LLM", "false"),
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
        model_name=os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct"),
        database_path=database_path(),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        confidence_threshold=_float("CONFIDENCE_THRESHOLD", 0.40),
        retrieval_top_k=_int("RETRIEVAL_TOP_K", 3),
        relevance_threshold=_float("RELEVANCE_THRESHOLD", 0.08),
        kill_switch=_flag("KILL_SWITCH", "false"),
        prometheus_port=_int("PROMETHEUS_PORT", 8000),
        development_tickets=ROOT / "data" / "development_tickets.json",
        documentation=ROOT / "data" / "documentation.json",
    )
