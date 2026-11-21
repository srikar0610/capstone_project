# Governance

## What the system must never do

- Send a reply that did not come from a retrieved passage.
- Send a reply after a guardrail block.
- Auto-answer a security incident, a compliance request, a feature request, or an unclear ticket.
- Put a secret, a card number or an email address into the outbound text.
- Follow instructions that arrive inside the ticket.

The mechanism is `src/guardrails.py` plus the never-auto list in `src/route.py`. `KILL_SWITCH=true` turns off every automatic send without a code change.

## Decision log

`storage/decisions.db`, table `decisions`. One `stage = final` row per ticket. Columns: decision id, time, ticket id, stage, prediction, confidence, threshold, action, reason, sources, guardrails, prompt version, requirement ids. The harness sets `decisions_match_tickets` by counting those rows against the file it just processed.

## Risk register

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| A fluent wrong answer reaches a customer | Medium | High | Send only quoted passages; block unsupported claims; confidence threshold | Support engineering |
| A security incident receives an automatic "try this" reply | Low if the classifier holds, high if it confuses the intent | High | Hard escalation for that intent, independent of the score | Support engineering |
| Private data echoed from a ticket into a reply | Low | High | The draft does not copy the ticket; the private-data check blocks if a pattern still appears | Support engineering |
| Provider outage stops the queue | Medium | Medium | Default path does not call a provider; a failed optional call degrades to the extractive draft | Support engineering |
| Uneven automation across regions or fluency | Medium | Medium | The metrics report compares automatic-reply rates by tier, region and fluency. A gap over five points is a release blocker | Support engineering |
| Threshold tuned until the validation file looks good | Medium | High | Classifier trains on the development file only. Validation is for the unattended run, not for fitting | Whoever changes a threshold |

## Fairness

The harness reports the automatic-reply rate by `customer_tier`, `customer_region` and `language_fluency`, and the gap between the highest and lowest group. The target is under five percentage points. A gap wider than that means the threshold or the training data is treating a group differently, and it should be read before any claim that the system is ready.

## Confidence

The calibration table in `metrics.json` bins stated confidence against how often the intent matched the label. If the 0.40–0.50 bin is correct only 20% of the time, the threshold is too low. That comparison is only present when the input file includes labels.

## Incident procedure

Use this at 02:00 without reading the code first.

1. Set `KILL_SWITCH=true` in `.env` and restart `python -m src.api`. Every new ticket escalates. Confirm with `GET /health`.
2. Stop any harness that is still sending replies. The process is the `evaluation.harness` command.
3. Open `storage/decisions.db` and read the latest `final` rows: ticket id, action, reason, sources, guardrails.
4. If a bad reply already went out, note the ticket id, the passage ids, and the guardrail result. Do not send a second automatic reply. A person writes the correction.
5. Leave the kill switch on until the reason is identified. A provider error is not, by itself, a reason to disable the guardrails.
6. Record the time the switch was turned on, the ticket ids involved, and what changed before it is turned off.

## Monitoring

`GET /metrics` on port 8000 exposes `tickets_processed_total`, `guardrail_blocks_total` and `response_seconds`. `prometheus.yml` scrapes that port. `grafana/dashboard.json` is a starter dashboard.
