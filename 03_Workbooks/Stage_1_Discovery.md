# Stage 1 — Discovery workbook

Evidence is the five transcripts in the pack and `data/development_tickets.json` (500 tickets). Counts below were computed from that file.

## 1. Interviews

| Who | What they told you | What they appear not to know | What you want to verify in the data |
|-----|--------------------|------------------------------|-------------------------------------|
| Marcus Adeyemi, Head of Support | More than 500 tickets a week, six agents, reply time 8–12 hours against a 2-hour agreement. First-contact resolution is 42%. He wants the easy tickets answered so people can do the hard ones. A wrong public answer is a failure. Enterprise customers and a compliance review both need an explanation of every decision. | He cannot break the queue down by topic. He reports the escalation rate and does not see what is inside those escalations. | Channel mix, intent mix, historical first-contact resolution, and whether "easy" means "already in the documentation". |
| Sofia Restrepo, Tier 1 | About seven in ten tickets are ones she has answered that month. Time goes on finding the article and writing it out, not on knowing the answer. Security is always escalated. Non-fluent tickets take longer and, she believes, have the worst satisfaction. | She thinks the documentation is fine and unused because search is bad. She does not have the count of how often a document already exists. | Share answerable from the 29 articles. Satisfaction by language fluency. |
| Daniel Okonkwo, Tier 2 | About half of what reaches him could have been closed in tier 1 with the right page and more confidence. Escalations arrive as the raw ticket, so he re-asks the customer. He wants a summary, a guessed topic, the relevant page, and the reason for doubt. He does not want automation trained on private snippet files, and he does not want automation on security, billing commitments, or data location. | He estimates "half" from last week's memory. Marcus's 42% figure is the one the file can check. | Historical escalation rate. Whether security, compliance and billing-like intents are marked must-not-auto-respond. |
| Ines Varga, Technical Writer | 29 support articles, reviewed on a rotation, covering auth, deployment, API, billing, data, security and accounts. Agents reconstruct her paragraphs from memory. Keyword search fails when the customer does not use the title words. She wants every answer to name the article. Feature requests, roadmap dates and novel incidents have no article. | She believes internal use is near zero. The ticket labels say whether a correct answer should cite those articles. | Count of articles in `documentation.json`. Share of tickets with `answerable_from_docs`. |
| Ravi Menon, Customer | Waiting until the next day is the problem. A pagination question can wait. A failed deployment cannot. He often finds the doc himself and then receives the same text hours later. An automated reply is acceptable if it cites the page and does not sound more certain than it is. He wants to know it was automated. A wider gap versus enterprise would show up at renewal. | He guesses he finds the answer half the time. The labelled set can say how often an article exists, not how often he personally finds it. | Urgency mix. Historical resolution time. Outcomes by customer tier. |

### Where the accounts disagree

| The disagreement | Who says what | How the data settles it | What follows |
|------------------|----------------|-------------------------|--------------|
| How much of the queue is already known | Sofia says about 70% are repeats she could answer. Marcus would be guessing at the topics. Ines thinks agents barely use the articles. | 357 of 500 tickets (71.4%) are `answerable_from_docs`. 0 tickets that are not answerable are labelled `auto_respond`. | The shortage is delivery of existing answers, not a shortage of answers. A chatbot that invents text does not fix that. |
| Whether escalations are the hard half | Daniel says about half of escalations were tier-1 work. Marcus treats the escalation rate as the cost problem and quotes 42% first-contact resolution. | History on the 500 tickets: first-contact resolution 219 (43.8%), escalated 281 (56.2%). Expected route is auto-respond on 311 (62.2%) and escalate on the rest. 46 tickets are answerable and still expected to escalate. | Closing the documentation tickets is the volume win. Finding a page is not, by itself, permission to send. |
| Who has the worst experience | Sofia says non-fluent tickets have the worst satisfaction and go round again. Ravi says the pain is urgency, not plan tier, and that enterprise already gets faster human replies. | Mean CSAT is 2.97 overall, 2.95 fluent (380) and 3.04 non-fluent (120). Historical first-contact resolution is 43.2% fluent and 45.8% non-fluent. By tier it is enterprise 37.3% (83), standard 43.1% (253), business 48.2% (164). Median historical resolution is 216 minutes. | Sofia's satisfaction claim is not in this file. The tier gap is. The design has to report automatic-reply rate by tier, region and fluency, and must not widen the enterprise gap on purpose. |

### What nobody said

| Never mentioned | Why you would have expected it | How you will check it |
|-----------------|--------------------------------|------------------------|
| Repeat contacts as a number | A wrong automatic close would create them. | 108 of 500 history rows are `repeat_contact` (21.6%). The system does not yet measure repeats after launch. |
| A kill switch | Marcus wants a wrong answer to be stoppable before the compliance review. | `KILL_SWITCH` escalates every new ticket without a code change. |
| The private snippet files as a training source | Daniel and Ines both warn about them. | The classifier trains on the labelled development tickets. The reply quotes `documentation.json` only. |

## 2. What the ticket data shows

| What to measure | Figure | Where it came from | What surprised you |
|-----------------|--------|--------------------|--------------------|
| Total tickets | 500 | `development_tickets.json` | Matches Marcus's weekly volume as a sample, not as a live week. |
| By channel | Email 212, chat 155, docs comment 78, forum 55 | `channel` | Chat is 31% and those rows have an empty subject. Ingest has to survive that. |
| By intent | 22 intents. Largest are data export and data residency (29 each). Smallest is rate limit (13). | `labels.intent` | Security (26) and compliance (26) are common enough to hard-code, not rare exceptions. |
| By urgency | Medium 226, high 146, low 128 | `labels.urgency` | High urgency is not the same as "must escalate". Deployment failures can be high and still labelled auto-respond. |
| Resolved on first contact | 43.8% (219) | `history.first_contact_resolution` | Sits on Marcus's 42%. |
| Average satisfaction | 2.97 / 5 | `history.csat_rating`, all 500 rows | The brief's 3.2 is the reported business figure. This file is slightly lower. |
| Most frequent single question | No single subject dominates. 155 chat rows have an empty subject. Next subjects are per-project spend caps (12) and CI connection (11). | `subject` | The repeated work is by intent, not by an identical subject line. |
| Answerable from documentation | 71.4% (357) | `labels.answerable_from_docs` | This is the design fact. |
| Non-fluent, and outcomes | 120 non-fluent (24%). First-contact resolution 45.8% versus 43.2% fluent. CSAT 3.04 versus 2.95. | `language_fluency`, history | Sofia's "worst satisfaction" claim is not supported here. |
| Outcomes by tier | Enterprise first-contact resolution 37.3%, standard 43.1%, business 48.2% | `customer_tier`, history | Enterprise is already the weakest historical resolution rate. |
| Repeat contacts | 21.6% (108) | `history.repeat_contact` | Nobody in the interviews gave this number. |

## 3. Where the time goes

| Category | Share of volume | Estimated share of effort | Why they differ | Evidence |
|----------|-----------------|---------------------------|-----------------|----------|
| Answerable from the 29 articles | 71.4% | Most of Sofia's minutes, little of Daniel's expertise | The answer exists. The minutes are search and rewriting. | Sofia's "four or five minutes" when she has seen it, "forty" when she has not. 357 labelled answerable. |
| Must-not-auto-respond (security, compliance, feature request, unclear) | 17.4% (87) | High per ticket, and it must stay human | A fast wrong answer is the failure Marcus named. | All 87 are `must_not_auto_respond`. Daniel names security, billing commitments and data location. |
| Answerable but still expected to escalate | 9.2% (46) | Agent judgement | A matching article is not sufficient. | Label cross-tab. |

Sofia's sequence:

| Step | What the agent does | Roughly how long | Could this be automated? |
|------|---------------------|------------------|--------------------------|
| 1 | Sort the queue by age | Minutes across the morning | No. The system should not reorder the human queue. It should take a ticket that is already submitted. |
| 2 | Read the channel text and work out the topic | A few minutes, longer when English is non-fluent | Yes, as a class plus a confidence and the alternatives. |
| 3 | Search for the article, or open a personal snippet file | The slow part of a known ticket | Yes, against Ines's 29 articles only. Not against snippet files. |
| 4 | Write the reply in the customer's words | Several minutes | Yes, only by quoting the passage and citing it. |
| 5 | Decide to send or escalate, with no note if escalating | Seconds to decide, expensive for Daniel afterwards | Yes. The escalation carries the summary, the sources and the reason. |

## 4. What the client counts as success

| Measure | Who watches it | Current value | What they would call success | Confidence |
|---------|----------------|---------------|------------------------------|------------|
| First-contact resolution | Marcus, internally | 42% reported; 43.8% in the file | He quoted an industry line of 65%. The pack target is 60%. | High on the baseline. The target is the pack's, not a promise. |
| Time to first reply | The service agreement, reported to executives | 8–12 hours | Under 2 hours contractually. The pack target for an automatic reply is under 5 minutes. | High. |
| Escalation rate | Marcus, as cost | About 58% in the brief; 56.2% escalated in history | 30% or lower in the evaluation framework | High on the baseline. |
| Customer satisfaction | Marcus | 3.2 / 5 reported; 2.97 mean in the file | 4.0 in the framework. This build does not invent a score. | Low until a person reviews a sample. |
| No public wrong answer | Marcus, as a veto | Not measured | He would rather the system say nothing | This is a guardrail, not a percentage. |

This project will have been worth doing if, within three months of launch, first-contact resolution is at least 60% and the first reply on documentation tickets is under five minutes, without an automatic reply on a security, compliance, feature or unclear ticket.

We will know it did not work if a customer receives a cited-looking answer the passage does not support, or if enterprise customers' automatic-reply rate falls far behind other tiers.

The measure Marcus is judged on internally is first-contact resolution. The measure in the contract is the two-hour first reply.

## 5. Data, constraints and risk

| Data source | What it contains | Quality and gaps | Access constraints | Private data? |
|-------------|------------------|------------------|--------------------|---------------|
| Support tickets | 500 development, 80 validation, channel, tier, region, fluency, labels, history | Labels exist on these files. The hidden 120 will not include a path you can tune on. | Development may be used to train. Validation is for a run, not for fitting. | Names and ids are in the file. The reply must not echo them. |
| Documentation | 29 articles | Ines says the reviewed set is current. Private snippets are not in it. | Retrieval reads this file only. | No. |
| Past resolutions | `history` and 200 ground-truth replies | Ground truth is a reference for claims that must not be made. It is not a generation target at runtime. | Do not train the reply on agent snippet files. | Some replies may mention customer-specific facts. Do not copy them into a new reply. |
| Customer records | Tier, region, fluency, name, id on each ticket | Enough to segment. Not a CRM extract. | Used for fairness counts, not for the text of the answer. | Yes. Keep them out of the outbound text. |

| What could go wrong | How likely | How bad | Who it affects | First prevention |
|---------------------|------------|---------|----------------|------------------|
| Confident and wrong | Medium | High | The customer who acts on it | Quote a passage or say nothing. Block unsupported claims. |
| Private data in a reply | Low if the draft does not copy the ticket | High | That customer | Pattern block, then escalate. Do not redact and send. |
| Some groups get worse answers | Medium | Medium | Enterprise, and any region the retriever matches poorly | Report the gap. Do not ship on a gap you have not read. |
| Articles go stale | Medium over a quarter | High | Anyone who receives the old steps | Cite the article id so Ines can correct the source. |

## 6. Problem statement

| Element | Statement | Supported by |
|---------|-----------|--------------|
| What the client asked for | A chatbot that answers tickets. | Marcus, "answering the easy ones". |
| What the evidence says they need | A way to send the article they already have, in seconds, and to hand a person the rest with the article and the reason attached. | 71.4% answerable. Sofia on search. Daniel on bare escalations. Ines on citations. |
| The gap | A chatbot will answer a security incident if the sentence is polite, and it will not show which article it used. | 87 must-not-auto-respond. Marcus on explainability. |
| Who is affected | Customers waiting 8–12 hours, six agents searching, tier 2 re-reading, Marcus reporting 42%. | Interviews and history. |
| What will change | Documentation tickets close without a person. The others arrive with a summary. | Routing rules and the escalation summary. |
| Not in scope | Replacing humans for security, compliance, feature requests and unclear tickets. A chat widget. A satisfaction score with no reviewer. | Daniel, Ines, the label field `must_not_auto_respond`. |

CloudServe does not have a shortage of answers. On this sample, seven in ten tickets are already answered in twenty-nine articles the team does not search. Customers wait eight to twelve hours, and fewer than half of tickets are resolved without another person. The work is to deliver the article when it applies, and to give a person the rest, with the reason written down. A chatbot that talks without that distinction will send the wrong thing and will not explain itself.

Marcus would recognise the waiting and the 42%. Sofia would recognise the search. Daniel would recognise the empty escalation. Ines would recognise the unused articles. Ravi would recognise that a deployment ticket and a pagination ticket are not the same wait. None of the five said the 71% figure. That figure is what joins them.
