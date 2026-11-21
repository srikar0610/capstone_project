# Stage 3 — Prompt library

The running system classifies and retrieves locally. The prompts are the specification of those steps. `USE_LLM=true` uses `generate_v1` as the system instruction. Versions are the strings written into the decision log. Full text is in `prompts/`.

## 1. From requirement to specification

| Requirement | Specification | Inputs | Outputs | Acceptance |
|-------------|---------------|--------|---------|------------|
| FR-ING-1 | Map email, live chat, documentation comment and community forum onto `email`, `chat`, `docs_comment`, `forum`. Preserve original text. | Raw JSON object or a non-object | One dict with `ticket_id`, `channel`, `original_text` | Four channels in one test. A non-object escalates. |
| FR-CLS-1 | Logistic regression on the development file only. Confidence is the class probability. Text under 12 characters returns `unclear_request` at 0.15. | Subject and body | Intent, urgency, confidence, alternatives | Confidence is between 0 and 1. Alternatives are present. |
| FR-RET-1 | TF-IDF over 800-character windows. Drop passages under `RELEVANCE_THRESHOLD` (0.08). | Ticket text, `documentation.json` | Ranked passages with `doc_id`, `passage_id`, text that is a slice of the article | An irrelevant query returns nothing. A known login question returns `DOC-AUTH-001`. |
| FR-GEN-1 | Quote the passages and append `[DOC-...]`. Do not copy the ticket into the reply. | Passages above the threshold | Answer, citations, or no draft | Every citation's id is in the retrieved set. |
| FR-RTE-1 | Send only if the intent is allowed, confidence is at least 0.40, a passage cleared the threshold, guardrails passed, and the kill switch is off. | Class, sources, guardrail result, settings | `sent` or `escalated`, plus a sentence | The same ticket twice matches. |
| FR-GRD-1 | Block injection, private data, and unsupported commitments. | Ticket text, outbound text, passages | Checks with `blocked` true or false | An injection ticket escalates and the customer does not receive the draft. |
| FR-LOG-1 | Insert one `final` row with the setup-guide columns. | The decision | SQLite row | Count of final rows equals tickets processed. |
| FR-RUN-1 | Read `--input`, write `metrics.json`, `metrics.md`, `tickets.jsonl` under `--output`. | A JSON list, or an object with a `tickets` list | The three files | A 3-ticket temp file produces all three groups of metrics. |

## 2. Prompt register

### classify-v1

| Field | Value |
|-------|--------|
| Name and purpose | Intent, urgency, confidence, alternatives |
| Category | Build |
| Serves | FR-CLS-1 |
| Version | classify-v1 |
| File | `prompts/build/classify_v1.txt` |
| Model | Not called at runtime. The local classifier implements the same output contract. |
| Inputs | One ticket as data |
| Output | JSON keys `intent`, `urgency`, `confidence`, `alternatives` |
| How you know it worked | A3. Short text falls back to `unclear_request`. |
| Weakness | It lists the 22 intents in the prompt. A new intent in the hidden set will be forced into this list or into the fallback. |
| Change history | Written with the requirement. Not revised. The implementation is the classifier, not a model call. |

### generate-v1

| Field | Value |
|-------|--------|
| Name and purpose | Grounded reply with citations |
| Category | Build |
| Serves | FR-GEN-1 |
| Version | generate-v1 |
| File | `prompts/build/generate_v1.txt` |
| Model | Optional OpenRouter model from `MODEL_NAME`, only when `USE_LLM=true` |
| Inputs | Passages and a ticket wrapped as untrusted data |
| Output | A short reply that keeps `[DOC-...]` citations, or an admission that the passages do not contain the answer |
| How you know it worked | A6. A provider failure keeps the extractive draft. |
| Weakness | The default path quotes passages instead of calling the model, because a free-form rewrite can drop the citation. |
| Change history | Version 1 of the PRD expected the model to write the reply. This prompt remains the instruction if the optional call is turned on. The shipped draft is the quotation. |

### route-v1

| Field | Value |
|-------|--------|
| Name and purpose | Send or escalate, with a readable reason |
| Category | Build |
| Serves | FR-RTE-1 |
| Version | route-v1 |
| File | `prompts/build/route_v1.txt` |
| Model | Not called. `src/route.py` is the rule. |
| Inputs | Intent, confidence, sources, guardrail flags, threshold, kill switch |
| Output | Action and a sentence |
| How you know it worked | A5. Security incidents escalate even at high confidence. |
| Weakness | The sentence is assembled from the rule that fired. It will not explain a nuance the rule does not encode. |
| Change history | Threshold in the surrounding config moved from the brief's 0.80 illustration to 0.40. The prompt still says `CONFIDENCE_THRESHOLD` rather than a hardcoded 0.80. |

### guardrails-v1

| Field | Value |
|-------|--------|
| Name and purpose | Block injection, private data, unsupported claims |
| Category | Build |
| Serves | FR-GRD-1 |
| Version | guardrails-v1 |
| File | Implemented in `src/guardrails.py`. Registered in `prompts/README.md`. |
| Model | None |
| Inputs | Ticket text, outbound text, passages |
| Output | A list of checks, each with `blocked` |
| How you know it worked | A7. Private-data and "a refund has been issued" both block in the unit test. |
| Weakness | Pattern lists miss private data that does not look like an email, a card or a key. |
| Change history | Written with the requirement. |

### judge-v1

| Field | Value |
|-------|--------|
| Name and purpose | Review grounding and citation match |
| Category | Evaluation |
| Serves | Evaluation framework, hallucination and citation accuracy |
| Version | judge-v1 |
| File | `prompts/evaluation/judge_v1.txt` |
| Model | Not called by the harness. The harness checks citation ids against retrieved passages in code. |
| Inputs | A reply and the passages it cites |
| Output | `grounded` and `citation_ok` |
| How you know it worked | The metrics file reports `citation_accuracy_percent`. A human still has to read a sample for hallucination. |
| Weakness | An automatic id check can pass while the sentence still overclaims the passage. |
| Change history | Added so the evaluation prompt exists as a file, which the setup guide requires. |

## 3. Traceability check

Every build prompt names its output fields, states what must not happen, and treats the ticket as data. Each requirement id in the decision log (`FR-ING-1` through `FR-LOG-1`) has a row above. The harness id `FR-RUN-1` is a command, not a prompt.
