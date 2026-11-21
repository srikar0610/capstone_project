"""The repository layout required by the setup guide and the submission guide."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "src/ingest.py",
    "src/classify.py",
    "src/retrieve.py",
    "src/route.py",
    "src/generate.py",
    "src/guardrails.py",
    "src/logging_store.py",
    "src/api.py",
    "prompts/README.md",
    "prompts/build/classify_v1.txt",
    "prompts/build/generate_v1.txt",
    "prompts/build/route_v1.txt",
    "prompts/evaluation/judge_v1.txt",
    "tests/test_system.py",
    "evaluation/harness.py",
    "evaluation/results/.gitkeep",
    "docs/architecture.md",
    "data/documentation.json",
    "data/development_tickets.json",
    "data/validation_tickets.json",
    ".github/workflows/ci.yml",
    "prometheus.yml",
    "grafana/dashboard.json",
]


def test_required_paths_exist():
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    assert missing == []


def test_gitignore_excludes_secrets_and_runtime_storage():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    lines = {line.strip() for line in text.splitlines()}
    assert ".env" in lines
    assert "storage/" in lines


def test_env_example_has_placeholders_only():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "OPENROUTER_API_KEY=your_key_here" in text
    assert "sk-" not in text
    for name in (
        "MODEL_NAME",
        "EMBEDDING_MODEL",
        "CHROMA_PATH",
        "DATABASE_URL",
        "LOG_LEVEL",
        "CONFIDENCE_THRESHOLD",
    ):
        assert name in text


def test_readme_documents_the_three_commands():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "python -m src.api" in text
    assert "python -m evaluation.harness --input" in text
    assert "--output" in text
    assert "python -m pytest tests/ -v" in text
