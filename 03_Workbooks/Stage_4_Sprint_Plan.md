# Stage 4 — Sprint plan

Individual project. One owner for every item: the author.

## 1. Capacity

| Week | Hours realistically available | Other commitments | Days you cannot work |
|------|-------------------------------|-------------------|----------------------|
| Week one | Discovery and the PRD before any feature work | Course reading on day one | Replace with your own calendar |
| Week two | Build, harness, one unattended run, revision | None recorded here | Replace with your own calendar |
| Week three | Governance, report, video, packaging | The video needs half a day, twice | Replace with your own calendar |

Anything blocked for more than an hour is written down the same day. The effort log is where those notes go. Hours in that log that you did not write yourself are marked unknown.

## 2. Backlog

| ID | Item | Est. hours | Priority | Depends on | Definition of done |
|----|------|------------|----------|------------|--------------------|
| B-01 | Environment and pins that install | 3 | Must | — | `pip install -r requirements.txt` succeeds. `.env` is gitignored before a key exists. |
| B-02 | Ingest | 3 | Must | B-01 | One ticket from each channel normalises. Empty body does not raise. |
| B-03 | Retrieval over the 29 articles | 5 | Must | B-02 | A known question returns a real `doc_id`. A nonsense query returns nothing. |
| B-04 | Classifier on the development file only | 5 | Must | B-02 | Intent, urgency, confidence, alternatives. Validation file is not in the fit. |
| B-05 | Harness with `--input` and `--output` | 4 | Must | B-02 | A small file writes `metrics.json` and `metrics.md`. |
| B-06 | Routing threshold and never-auto intents | 3 | Must | B-04 | Same ticket twice, same decision. Security escalates. |
| B-07 | Cited draft | 4 | Must | B-03 | Citations resolve to retrieved passages. |
| B-08 | Guardrails that block | 4 | Must | B-07 | Injection, private data and an unsupported refund claim block. |
| B-09 | Decision log | 3 | Must | B-06 | One final row per ticket. Columns match the setup guide. |
| B-10 | API, metrics, CI | 3 | Must | B-09 | `python -m src.api`. `pytest` in GitHub Actions. Prometheus scrape on port 8000. |
| B-11 | Unattended validation run | 2 | Must | B-05, B-10 | 80 tickets, no restart. Report saved under `evaluation/results/`. |
| B-12 | PRD revision | 2 | Must | B-11 | At least one substantive change with its trigger. |
| B-13 | Governance write-up | 3 | Should | B-09 | Risk register, fairness, incident steps, kill switch. |
| B-14 | Video and report | 8 | Must | B-11 | Follow the section order and the recording guide. |

If time runs out, drop B-13's dashboard polish and the optional model rewrite. Do not drop B-05 or B-11. A system that has never processed the file in one run does not clear the gate.

## 3. Week two, day by day

| Day | What must work | Check |
|-----|----------------|-------|
| 1 | Ingest | Print one normalised ticket per channel |
| 2 | Retrieval | Query a known article and confirm the passage text is a slice of it |
| 3 | Classification and routing | Twenty tickets. Every log row has a reason. |
| 4 | Generation and guardrails | The injection ticket is blocked |
| 5 | Full chain | Start the harness, leave it, come back to a metrics file |

## 4. What was dropped

LangChain 0.1 and Chroma 0.3, because those pins do not install on the Python used here. Retrieval is TF-IDF. The optional OpenRouter call stays off so a free-tier outage cannot fail the run. That departure is recorded in `docs/architecture.md`.

## 5. Daily check-in

| Day | Done | Blocked | Decision |
|-----|------|---------|----------|
| Build days | The modules in `src/` and the tests | Pack pins would not install | Keep the local index and document it |
| Evaluation day | 80-ticket run on 21 November 2026 | Hidden file is not in the pack | Report the validation run and say the hidden set was not used |
