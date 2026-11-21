# Stage 5 — PRD revision log

Compulsory. Version 2 is what the code implements. The short form also lives in `docs/requirements.md`.

## 1. Summary

| Field | Value |
|-------|--------|
| New version | 2.0 |
| Date | During the build, after the 0.80 threshold was compared with class probabilities on the development file |
| Who revised | praveenkumarkundarapu |
| Who agreed | Individual project. No second reviewer. |
| Requirements changed | FR-GEN-1, FR-RTE-1, NFR-07 |
| Requirements added | None. FR-RUN-1 was already in version 1 because the hidden file is not local. |
| Requirements removed | None |

## 2. The changes

| ID | Version 1 | Version 2 | What prompted it | Agreed by |
|----|-----------|-----------|------------------|-----------|
| FR-GEN-1 | One model call classifies the ticket and writes the reply. | The reply is a quotation of retrieved passages with `[DOC-...]` citations. A model rewrite is optional and off by default. | A generated sentence could not be checked by following the citation to a passage the retriever returned. A6 fails if the citation is only plausible. | Author, after A6 was written as a test that opens the article |
| FR-RTE-1 | Send when confidence is at least 0.80, the figure in the brief's diagram. | Send when confidence is at least 0.40, a passage cleared 0.08, the intent is not one of the four never-auto intents, guardrails pass, and the kill switch is off. High-urgency database and performance tickets escalate. | On 22 intents the class probability rarely clears 0.80, so the 8–12 hour queue would not move. High-urgency deployment failures are often labelled auto-respond. Database and performance at high urgency were the ones a person still took. | Author, from the development labels, not from the validation file |
| NFR-07 | Use the pinned LangChain and Chroma stack. | Use a local TF-IDF index. The unattended run must not depend on an embedding download or a paid call. | The pack's 2024 pins do not install on this Python. | Author, on day one of the build |

## 3. Assumptions that did not hold

| Assumption in version 1 | Did it hold? | What you found | What changed |
|-------------------------|--------------|----------------|--------------|
| One model call can both classify and answer | No | Citation checks need the passage text the retriever actually returned | Split classify, retrieve, quote |
| 0.80 is a workable send bar | No | It escalates almost everything | Threshold 0.40, stored on every decision row |
| Every high-urgency ticket should escalate | No | Urgency and "must escalate" are different labels | Escalate high-urgency database and performance only, plus the four never-auto intents |
| The setup-guide vector store will install | No | No wheels for the pinned Chroma on this interpreter | TF-IDF, documented in the architecture note |

## 4. What was left unchanged

| What looked wrong | Why it stayed | Cost of changing | Revisit when |
|-------------------|---------------|------------------|--------------|
| Classification macro precision of 1.0 on the 80 visible validation tickets | That number is not evidence about the hidden file. Lowering it by hand would be tuning. | A different model, fitted without the validation file, then one more stated run | The single hidden-set run |
| Fairness gap of 29 points by customer tier on that same 80 | The gap is real on this file and is reported. Changing the threshold to flatten it would be fitting the validation file. | A stratified error analysis on the development file only | Before any claim that NFR-06 is met |
| No human satisfaction score | Inventing 4.0 would fail the evaluation section | A 50-reply review by two people | Before the report claims satisfaction |

## 5. Reflection

Version 1 misunderstood the problem as "call a model with a high confidence bar". The transcripts already said the articles exist and the search does not. The 71.4% figure would have caught that before the threshold argument, if it had been treated as a design constraint rather than as a background statistic.

Starting again on Monday, the harness and the citation test would be the first code, and the model call would be the last. What is still uncertain is how the hidden 120 tickets differ from these 80, and whether 0.40 is calibrated on tickets the classifier has not seen. Resolving that takes one unattended run on the hidden file, reported with the date, and a calibration table on that output.
