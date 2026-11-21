# Architecture

Six stages run in order for every ticket. Three concerns sit across all of them: the decision log, the guardrails, and the Prometheus counters.

```
ticket -> ingest -> classify -> retrieve -> draft -> guardrails -> route -> log
```

| Stage | Module | What it guarantees |
|-------|--------|--------------------|
| Ingest | `src/ingest.py` | Email, chat, documentation comments and the forum become one record. The original text and the channel are kept. Missing fields do not raise. |
| Classify | `src/classify.py` | Intent, urgency, a probability, and the alternatives considered. Text shorter than 12 characters falls back to `unclear_request`. |
| Retrieve | `src/retrieve.py` | Ranked passages with `doc_id` and `passage_id`. The passage text is an exact slice of the article. Weak matches are discarded. |
| Draft | `src/generate.py` | A reply built from those slices, with citations. The ticket is the search query. It is not copied into the reply. |
| Guardrails | `src/guardrails.py` | Injection, private data, unsupported claims. Any hit blocks the send. |
| Route | `src/route.py` | Send or escalate. The reason is a sentence, not a flag name. |
| Log | `src/logging_store.py` | One `final` row per ticket in SQLite, with the schema from the setup guide. |

`src/pipeline.py` is the orchestrator. `src/api.py` is a FastAPI wrapper around the same function the harness calls, so a single ticket and the unattended file take the same path.

## Why this is not a chatbot

A chatbot will answer a security incident if the sentence is polite enough. The development set marks all 26 security incidents, all 26 compliance requests, all 20 feature requests and all 15 unclear requests as must-not-auto-respond. Those four intents escalate even when retrieval finds a related article. The article still goes to the agent in the escalation summary.

## Departures from the pinned stack

The pack pins LangChain 0.1.0, LangGraph 0.0.20 and Chroma 0.3.21. Those builds do not install on Python 3.14, and Chroma's embedding download makes the first unattended run depend on a large model fetch. Retrieval here is scikit-learn TF-IDF, persisted only in memory for the process. Citations still resolve to real `doc_id` values. The optional OpenRouter call in `src/llm.py` is off by default so a free-tier outage cannot fail the gate (criterion A11). Turn it on with `USE_LLM=true` after placing a key in `.env`.

## Thresholds

| Knob | Default | Effect of going lower | Effect of going higher |
|------|---------|----------------------|------------------------|
| `CONFIDENCE_THRESHOLD` | 0.40 | More automatic replies, including ones the classifier is unsure about | More escalations, closer to today's 58% escalation rate |
| `RELEVANCE_THRESHOLD` | 0.08 | More passages, some of them loosely related | More "I do not know", which is the correct outcome for a weak match |
| `RETRIEVAL_TOP_K` | 3 | — | One passage per article, so three articles at most |

The 0.80 figure in the brief is an illustration. Twenty-two intent classes do not produce 0.80 probabilities often enough for that cutoff to change CloudServe's queue. 0.40 is the working cutoff, and it is recorded on every decision row.

## Failure behaviour

| Condition | What happens |
|-----------|----------------|
| Empty or non-object ticket | Escalated as `unclear_request` |
| No passage above the threshold | Escalated. Nothing is invented |
| Provider timeout, HTTP 429, or missing key | Extractive draft kept, `model_degraded` set, run continues |
| Kill switch | Every ticket escalates |
| Guardrail hit | Customer receives the escalation notice, not the draft |
