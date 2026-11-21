# Prompt register

The running system classifies and retrieves locally, then drafts by quoting passages.
These prompts are the specification for those steps. The optional model path
(`USE_LLM=true`) uses `generate_v1` as its system instruction. Versions below are
the ones written into the decision log.

| ID | Version | File | Purpose | Requirement |
|----|---------|------|---------|-------------|
| classify | classify-v1 | build/classify_v1.txt | Intent, urgency, confidence, alternatives | FR-CLS-1 |
| generate | generate-v1 | build/generate_v1.txt | Grounded reply with citations | FR-GEN-1 |
| route | route-v1 | build/route_v1.txt | Send or escalate, with a readable reason | FR-RTE-1 |
| guardrails | guardrails-v1 | implemented in src/guardrails.py | Block injection, private data, unsupported claims | FR-GRD-1 |
| judge | judge-v1 | evaluation/judge_v1.txt | Human or model review of grounding | Evaluation framework |

A prompt is kept only when it names the output fields, states what the model must not do, and treats the ticket as data rather than as an instruction.
