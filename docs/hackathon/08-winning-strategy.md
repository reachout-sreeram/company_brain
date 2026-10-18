# Winning strategy

Status: partly superseded. The proposition, build sequence, and demo below describe the earlier PromiseGraph candidate. The current build order and demo script are in the [Stage 2 success definition](../planning/15-stage-2-success-definition.md#build-order). The guidance on differentiation claims, the submission package, and the risks remains useful.

Build a small, credible Company Brain workflow. Winning is uncertain. There is no published numeric rubric in the reviewed event pages, and research cannot guarantee a prize.

## The proposition

“When a release plan changes, PromiseGraph finds the customer promises that need review, explains each dependency, and prepares the next task for the current owner.”

That statement is concrete enough to test. It avoids competing with an entire company-search platform. It also makes graph necessity visible in a short demonstration.

## What the judges should be able to inspect

The result should visibly depend on a graph query. The source path must support each finding. A new fact must change the result. A replay must preserve state without duplicating actions. A graph outage must stop unsupported answers.

The [sponsor's previous recap](https://www.falkordb.com/blog/how-builders-at-hack-for-humanity-used-falkordb-to-solve-real-community-problems/) gives useful examples of inspectable queries and reproducible behavior. It is a precedent, not this event's official judging rubric.

## Build sequence

The event closes on 18 October at 11:59 PM IST. The plan below assumes a solo builder or small team starting on 15 October evening. Re-plan against actual available hours. A reasonable target is 24–32 focused implementation hours plus a submission buffer, not every remaining clock hour.

| Window, IST | Deliverable | Exit condition |
| --- | --- | --- |
| 15 October evening | Narrow scope, graph spike, original source corpus | Tested client, query, update, restart; reviewed truth table |
| 16 October first work block | Ingestion and current-state graph | Validated extraction; idempotency; provenance |
| 16 October second work block | Impact and owner tools | Direct, indirect, unaffected, exception, unknown cases pass |
| 17 October first work block | Thin UI and evidence views | User can inspect every finding and source |
| 17 October second work block | Actions, replay, stale-draft checks | Local task changes persist correctly |
| 18 October first work block | Evaluation and fixes | Published raw results and honest limits |
| 18 October afternoon/evening | README, recording, setup or deployment | Reproduce from clean state; submission prepared |
| Before 18 October, 10:30 PM | Submit target | Buffer before official close |

The submission target is ours. The actual official deadline remains 11:59 PM IST, as stated in the [schedule](https://www.wemakedevs.org/hackathons/falkordb/schedule).

Time-box the SDK decision to roughly 60–90 minutes. If a framework does not pass update and source-lineage tests, use direct extraction and explicit Cypher. Do not spend half the event integrating a general memory platform.

## Priority order and cuts

P0 is the graph, one real text-to-fact extraction, five differentiated commitment outcomes, evidence, and persistence. P1 is local task review, stale-draft prevention, and a fair baseline. P2 is historical queries, a second track, deployment polish, and a blog post.

If behind, cut live connectors, whole-company search, multi-agent orchestration, elaborate graph animation, and general-purpose workflow editing. Keep the actual agent loop and graph integration. Never replace them with a hidden hardcoded impact list.

## Suggested demo, about three minutes

This length is our recommendation. No official duration was established by the reviewed pages.

| Time | Scene | Proof |
| --- | --- | --- |
| 0:00–0:20 | Show a release ticket, a promise, and a separate dependency note | The answer crosses sources |
| 0:20–0:45 | Ask which promises need review; show the initial result | Working graph retrieval |
| 0:45–1:15 | Ingest a new approved date change; inspect extracted facts | Actual update, not a UI toggle over canned answers |
| 1:15–1:45 | Show two impacted, one later-due, one exception, one unknown | Useful precision and uncertainty |
| 1:45–2:10 | Open the indirect path and current owner evidence | Relationship and source correctness |
| 2:10–2:35 | Review a local follow-up task; replay the event | Durable outcome and no duplicate |
| 2:35–3:00 | Show measured baseline results and limits | Honest evidence for the architecture |

Keep a recorded failure check or a short appendix showing that a database outage stops results. Do not risk the main recording on an untested outage-recovery sequence.

The participant should explain the schema, the main query, one false-positive case, and why source authority is separate from recency. That demonstrates meaningful technical understanding.

## Differentiation that survives research

Use this claim: “We focus on reconciling dated customer promises after release changes. We expose unknown dependencies, scoped exceptions, current owners, and stale action drafts.”

Do not use these claims: first company brain, first temporal graph memory, first graph-based change-impact agent, competitors cannot act, graphs eliminate hallucinations, or no graph path means no business risk. The research does not support them.

Credit close inspiration, especially [Drift](https://github.com/sharique2004/mmm-demo) and [Hopper](https://github.com/vraj00222/hopper), if the implementation follows their concepts. Write new code and original fixtures. Clearly identify reused code and its license if any is adopted. None has been copied into this workspace.

## Public submission package

Use the compliance checklist in [rules and expectations](01-hackathon-rules.md). Our additional recommendation is to include a short architecture explanation, an explicit synthetic-data notice, measured results, a query walkthrough, known failures, pinned versions, and an AI-assistance disclosure that describes what the participant reviewed and changed.

Prefer a deployment only if it works reliably and keeps database credentials server-side. Otherwise, complete local instructions and a working video are the allowed route. Do not advertise an unverified URL as a live application.

For the optional blog, explain the user problem, one graph query, one incorrect early result, the fix, and the evaluation. A concrete engineering story is more credible than a list of sponsor features.

## Main risks

| Risk | Detection | Response |
| --- | --- | --- |
| Too close to earlier projects | Side-by-side workflow comparison | Keep explicit commitment feasibility and state tests; avoid novelty claims |
| Extraction invents a dependency | Unsupported source span | Reject candidate; keep unknown |
| Synthetic corpus is too easy | Baseline already answers everything | Add realistic ambiguity and held-out structure, not artificial sabotage |
| Graph adds no measured benefit | Baseline equals or exceeds results | Report it; narrow claims to inspectability or update correctness |
| Action uses obsolete facts | Evidence revision changed | Regenerate before approval |
| Scope grows | Core cases still failing by 17 October | Cut P2 and extra connectors |
| Cost grows | Extraction or retry count exceeds cap | Batch, cache unchanged sources, reduce corpus size |

## Decision status

The research supports building a focused prototype. It does not support a claim of commercial differentiation or customer willingness to pay. Treat the hackathon as a test of execution and a starting point for user discovery.
