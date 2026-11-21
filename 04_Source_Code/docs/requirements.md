# Requirements (v1, revised)

Each requirement points at the discovery evidence that produced it.

| ID | Requirement | Evidence | Where it lives |
|----|-------------|----------|----------------|
| FR-ING-1 | Accept email, chat, documentation comments and the forum into one record, and keep going when fields are missing. | Four channels in the ticket file; chat subjects are often empty. | `src/ingest.py` |
| FR-CLS-1 | Assign intent and urgency with a probability and the alternatives considered. Fall back to `unclear_request` instead of raising. | 22 intents. Unclear tickets are never auto-answered. | `src/classify.py` |
| FR-RET-1 | Retrieve passages whose identifiers exist in the 29-article corpus. Return nothing below the relevance threshold. | 71% of tickets are answerable from those articles. | `src/retrieve.py` |
| FR-GEN-1 | Draft only from retrieved passages, with citations, and keep the ticket out of the instruction channel. | Citation accuracy target 95%. Ground-truth replies forbid invented claims. | `src/generate.py` |
| FR-RTE-1 | Send or escalate with a deterministic rule and a reason a manager can read. | Auto-reply is expected on 62%, never on the four must-not intents. | `src/route.py` |
| FR-GRD-1 | Block, not warn, on injection, private data and unsupported claims. | Governance condition: zero private data in outbound text. | `src/guardrails.py` |
| FR-LOG-1 | Write every final decision to SQLite with the setup-guide columns. | Decision logging must reconcile with tickets processed. | `src/logging_store.py` |
| FR-RUN-1 | One command processes a path it is given and writes the metrics file. | Hidden set of 120 is not in the pack. | `evaluation/harness.py` |

## Out of scope

- Replacing the human team for security, compliance or feature requests.
- A customer-facing chat widget. The API is the interface; channel adapters can post the same JSON.
- Live customer-satisfaction collection. The report says so rather than inventing a score.
- Training on `validation_tickets.json`.

## Revision

v1 assumed a single model call that both classified the ticket and wrote the reply, with 0.80 as the send threshold because that number is in the brief's diagram.

That failed contact with the data. Class probabilities over 22 intents rarely clear 0.80, so the threshold would have escalated almost everything and left the 8–12 hour queue intact. A free-form model reply also could not meet the citation check, because the citation has to be a passage the retriever returned.

v2 separates classification, retrieval and a quoted draft, lowers the working threshold to 0.40, and hard-escalates the four intents that are never safe to send. High-urgency database and performance tickets also escalate: on the development set those were the high-urgency intents a person still took, which was not true of high-urgency deployment failures. The decision log stores the threshold that was actually used.
