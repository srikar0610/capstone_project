# Discovery notes

Evidence is the development file (500 tickets) and the documentation corpus (29 articles). The stakeholder transcripts in the pack are the qualitative half of this; the counts below are the half that can be checked.

## What the queue actually contains

| Signal | Count | Share |
|--------|------:|------:|
| Tickets | 500 | 100% |
| Email / chat / docs comment / forum | 212 / 155 / 78 / 55 | 42% / 31% / 16% / 11% |
| Answerable from documentation | 357 | 71% |
| Expected automatic reply | 311 | 62% |
| Expected escalation | 189 | 38% |
| Must not auto-respond | 87 | 17% |

Must-not-auto-respond is exactly four intents: compliance (26), security incident (26), feature request (20), unclear (15). No ticket that is not answerable from the docs is expected to be auto-answered. 46 tickets are answerable and still expected to escalate, so "we found a document" is not a sufficient reason to send.

## Problem statement

CloudServe's first-reply time is 8–12 hours against a 2-hour agreement, and first-contact resolution is 42%. The volume is not 500 novel engineering problems a week. Most of it is a question the documentation already answers, sitting in the same queue as a smaller set of tickets that must reach a person (security, compliance, product requests, and anything the team cannot classify). A chatbot does not separate those. It also does not record why it answered.

The system CloudServe needs is a documentation router: reply in seconds when a passage supports the answer, and escalate the rest with the passage, the predicted intent, the confidence and the reason already attached.

## What would change the design

If the share of documentation-answerable tickets on the hidden set were much lower than 71%, the confidence threshold should move up and the automatic-reply rate would fall. That is a measurement outcome, not a reason to answer without a source.
