# Data

These files are copied from the capstone pack.

| File | Role |
|------|------|
| development_tickets.json | 500 labelled tickets. The classifier trains on this file only. |
| documentation.json | 29 articles. The retrieval index is built from this file only. |
| ground_truth_responses.json | 200 senior-agent replies. Reference for what not to claim. Not used at runtime. |
| validation_tickets.json | 80 tickets for a local unattended run. Do not tune the system against this file. |

The hidden 120-ticket set is not here. Point the harness at it with `--input`.
