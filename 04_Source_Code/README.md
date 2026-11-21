# CloudServe support system

CloudServe asked for a chatbot. The ticket data says something else. On the 500 development tickets, 357 (71%) are already answered in CloudServe's own documentation, and every ticket labelled `security_incident`, `compliance_request`, `feature_request` or `unclear_request` is marked must-not-auto-respond. This system answers the first group from the documentation, with citations, and hands the second group to a person with the passages and the reason attached.

It is a local pipeline. It does not need an API key to run the acceptance checks.

## What you need

- Python 3.10 or later (developed on 3.14, CI uses 3.11)
- Git
- About 1 GB of free disk for the virtual environment

## Setup

From this directory:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
```

macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Leave `OPENROUTER_API_KEY` as `your_key_here` and `USE_LLM` as `false` unless you have a free OpenRouter key and want the optional rewrite step. Do not commit `.env`.

## Run

Start the API:

```bash
python -m src.api
```

Submit one ticket:

```bash
curl -X POST http://127.0.0.1:8000/tickets -H "Content-Type: application/json" -d "{\"ticket_id\":\"DEMO-1\",\"channel\":\"email\",\"subject\":\"Invalid credentials\",\"body\":\"The console returns Invalid credentials despite a correct password.\"}"
```

Health check: `http://127.0.0.1:8000/health`. Metrics: `http://127.0.0.1:8000/metrics`.

Prometheus scrapes `http://localhost:8000/metrics` using `prometheus.yml`. A starter Grafana dashboard is in `grafana/dashboard.json`.

## Unattended evaluation

The harness takes the paths you pass. It does not look for a hardcoded filename.

```bash
python -m evaluation.harness --input data/validation_tickets.json --output evaluation/results
```

That writes `metrics.json`, `metrics.md` and `tickets.jsonl`. Use the same command with the hidden ticket file when you have it. One bad ticket is escalated and the run continues. If the model provider is enabled and then fails, the ticket still finishes on the extractive draft.

## Tests

```bash
python -m pytest tests/ -v
```

## Layout

This is the layout from the setup guide. Extra modules sit in the same folders.

```
README.md
requirements.txt
.env.example
.gitignore
prometheus.yml
src/
  ingest.py  classify.py  retrieve.py  route.py
  generate.py  guardrails.py  logging_store.py  api.py
  pipeline.py  config.py  llm.py  metrics_prom.py  logging_config.py
prompts/
  build/          prompts that run inside the system
  evaluation/     prompts used to judge output
  README.md       the register, with versions
tests/
evaluation/
  harness.py      unattended run; takes --input and --output
  report.py       metrics file written at the end of that run
  results/        dated output from each run
docs/
  architecture.md
data/             pack datasets used by the documented commands
grafana/
  dashboard.json
storage/          generated at runtime, not committed
.github/workflows/ci.yml
```

## Design choices you will be asked about

- Retrieval is TF-IDF over 800-character windows of `documentation.json`, with a relevance threshold. The pack's Chroma 0.3 pin does not install on current Python, and a local index keeps the unattended run inside the free tier. Passages below the threshold are dropped.
- Classification is a logistic regression trained only on `development_tickets.json`. Confidence is the class probability. The validation file is not used for training.
- Routing sends a reply only when confidence is at least `CONFIDENCE_THRESHOLD` (0.40), a passage cleared the relevance threshold, the intent is not one of the four never-auto intents, guardrails pass, and the kill switch is off. The same inputs produce the same decision.
- Guardrails block prompt injection, private data in the outbound text, and claims the passages do not support (`a refund has been issued`, `fixed on our side`, a delivery date). A block escalates. The customer does not receive the blocked draft.
- Set `KILL_SWITCH=true` to escalate every ticket.

## Attribution

The pipeline was written for this capstone with assistance from Cursor's coding agent (Grok). The judgement about what to automate, the thresholds, and the never-auto intents come from the development tickets and the pack, not from an invented support story. Libraries are listed in `requirements.txt`.

## Submission pack

`submission/CHECKLIST.md` lists every item the Word documents require. The archive name is `praveenkumarkundarapu_Capstone_Submission.zip`. The report and workbooks are exported as PDF and DOCX. The video is still to be recorded.

## More detail

- `docs/architecture.md`
- `docs/discovery.md`
- `docs/requirements.md`
- `docs/governance.md`
