# Stage 2 — Product requirements

## 1. Document control

| Field | Value |
|-------|--------|
| Version | 1.0, revised to 2.0 in the Stage 5 log |
| Written by | praveenkumarkundarapu |
| Date | Version 1 at the end of discovery. Version 2 after the threshold failed on the development labels. |
| Status | Version 2 is the one the code implements |
| Approved by | Individual project. No second reviewer. |

## 2. Problem statement

CloudServe does not have a shortage of answers. On the 500 development tickets, 357 are already answered in twenty-nine articles the team does not search. Customers wait eight to twelve hours, and fewer than half of tickets are resolved without another person. The work is to deliver the article when it applies, and to give a person the rest, with the reason written down.

## 3. Who this is for

| User group | What they need | What they do now | How you will know |
|------------|----------------|------------------|-------------------|
| Customers | A correct reply the same day, with the page it came from, or an honest handoff | Wait 8–12 hours, often after finding the page themselves | Reply time on sent tickets. Citations present. No unsupported claim. |
| Tier 1 agents | The search and the first draft done, and security never sent | Personal snippet files and a painful search | Escalations arrive with a summary and sources. |
| Tier 2 | Context, not another copy of the raw ticket | Re-read and re-ask | The escalation summary names intent, confidence, sources and reason. |
| Head of support | First-contact resolution up, and a reason for every automatic decision | A red 42% and no topic breakdown | The metrics file and a decision row per ticket. |

## 4. Functional requirements

| ID | Requirement | Priority | Discovery evidence | Acceptance |
|----|-------------|----------|--------------------|------------|
| FR-ING-1 | Accept email, chat, documentation comments and the forum as one record. Keep the original text and the channel. Missing fields do not raise. | Must | Four channels. 155 chat subjects empty. | A2 |
| FR-CLS-1 | Assign intent and urgency, a probability, and the alternatives. Too-short text becomes `unclear_request`. | Must | 22 intents. Unclear is never auto-answered. | A3 |
| FR-RET-1 | Return passages that exist in the 29 articles, or return nothing below the relevance threshold. | Must | 71.4% answerable. Ines on title search. | A4 |
| FR-GEN-1 | Draft only from those passages, with citations. The ticket is data, not an instruction. | Must | Marcus on wrong answers. Ines on naming the article. | A6 |
| FR-RTE-1 | Send or escalate with one threshold, the same decision on the same input, and a reason a manager can read. Never auto-send security, compliance, feature request or unclear. | Must | 87 must-not-auto-respond. 46 answerable tickets still expected to escalate. | A5 |
| FR-GRD-1 | Block, not warn, on prompt injection, private data and unsupported claims such as a refund, a fix already applied, or a delivery date. | Must | Marcus's veto. Daniel on billing commitments. | A7 |
| FR-LOG-1 | Write one final decision row per ticket with the setup-guide columns, including prompt version and requirement ids. | Must | Marcus's compliance review. | A8 |
| FR-RUN-1 | One command reads a ticket path it is given and writes the metrics file. One bad ticket does not stop the file. | Must | Hidden set of 120 is not in the pack. | A9, A10, A11 |

## 5. Non-functional requirements

| ID | Category | Requirement | How it is verified |
|----|----------|-------------|--------------------|
| NFR-01 | Latency | 95th percentile under 3 seconds on the local path | `latency_seconds_p95` in the metrics file |
| NFR-02 | Availability | A provider timeout, a 429, a missing key or a malformed ticket still produces a decision | A11 tests |
| NFR-03 | Accuracy | Classification precision 85% or better on a set the model was not fitted to. Citation accuracy 95% where citations exist. | Metrics file. The visible validation file is not the hidden set. |
| NFR-04 | Privacy | Zero private data in outbound text | Guardrail plus `private_data_detections` |
| NFR-05 | Auditability | Logged decisions equal tickets processed | `decisions_match_tickets` |
| NFR-06 | Fairness | Automatic-reply rate varies by less than 5 points across tier, region and fluency | `fairness_auto_answer_rate` |
| NFR-07 | Cost | The unattended run does not require a paid model | `USE_LLM=false` by default |

## 6. Out of scope

| Not building | Why not | Reconsider when |
|--------------|---------|-----------------|
| A customer-facing chat widget | The failure is routing and evidence, not a new channel | A channel adapter can already post the same JSON |
| Automatic answers for security, compliance, feature requests, unclear tickets | The labels forbid them. Daniel and Marcus both treat a wrong send as the failure mode | A human policy change, not a model change |
| Training on agent snippet files or on the validation file | Daniel and Ines. The hidden set is the grade. | Never for the validation file |
| A live satisfaction score | There are no live customers in this exercise | A reviewed sample of at least 50 replies, two readers |

## 7. Assumptions in version 1

| Assumption | Why it seemed true | If it is false | How you find out |
|------------|--------------------|----------------|------------------|
| One model call can classify and write the reply | The brief is about a language model | Citations will not resolve to retrieved passages | Follow a citation. A6 fails. |
| A send threshold of 0.80 is the right cutoff | The brief's diagram uses 0.80 | 22-way probabilities rarely clear 0.80, so the queue does not move | Read the confidence distribution on the development file |
| Any high-urgency ticket should escalate | Ravi's deployment story | High-urgency deployment failures are often labelled auto-respond. High-urgency database and performance tickets are the ones a person still took | Cross-tab urgency and intent against `expected_route` |
| Chroma and the pack's LangChain pins will install | The setup guide says so | They do not install on current Python without a compiler | The install on day one |

## 8. Success measures

| Measure | Baseline | Target | Measured how | Reported by |
|---------|----------|--------|--------------|-------------|
| First-contact resolution | 42% | 60% or better | Share of tickets sent from documentation with no person | The harness |
| Time to first reply | 8–12 hours | Under 5 minutes | Processing time on the automatic path | The harness |
| Customer satisfaction | 3.2 / 5 | 4.0 | Not measured automatically | A human review, stated as missing |
| Escalation rate | 58% | 30% or lower | Share escalated or blocked | The harness |

## 9. Open questions

| Question | Why it matters | Owner | Resolve by |
|----------|----------------|-------|------------|
| Will the hidden 120 look like the 71% documentation share? | If not, the automatic rate will fall and that is the correct outcome | Author | When the harness is pointed at that file, once |
| Is 0.40 calibrated? | A threshold that does not match observed accuracy will send work the classifier cannot do | Author | Calibration bins in the metrics file, on a set that was not used for training |
| Who signs the kill switch in production? | The procedure names the mechanism. CloudServe has not named a person. | Marcus, outside this exercise | Before any real customer traffic |
