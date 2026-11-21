import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORAGE = ROOT / "storage"
STORAGE.mkdir(parents=True, exist_ok=True)
database = STORAGE / "pytest_decisions.db"
if database.exists():
    database.unlink()

os.environ["DATABASE_URL"] = "sqlite:///" + database.as_posix()
os.environ["USE_LLM"] = "false"
os.environ["KILL_SWITCH"] = "false"
os.environ["CONFIDENCE_THRESHOLD"] = "0.40"
os.environ["RELEVANCE_THRESHOLD"] = "0.08"
os.environ["RETRIEVAL_TOP_K"] = "3"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["OPENROUTER_API_KEY"] = "your_key_here"
