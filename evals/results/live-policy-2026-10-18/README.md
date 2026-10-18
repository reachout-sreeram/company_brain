# Method-specific comparison policy — v4.2

Independent review found an introduced confound in [v4.1](../live-corrections-2026-10-18/README.md): its shared prompt instructed search to call assess_retirement, although that tool was absent. Search clear-state relied on that unavailable requirement and falsely claimed exhaustion after 10/12 calls. The historical cohort is explicitly marked confounded; its raw bytes and original scores are unchanged. This separate run verifies the policy correction, not a general graph advantage.

## Correction and verification

Implementation **0b2ddea** separates the two method instructions. Graph uses and preserves its available assessment. Search explicitly derives its own verdict from accessible source/assertion records under the shared scope, time, freshness, authority, supersession and inventory rules; no consolidated assessment action is required. Search policy, native final-function instructions and host budget/empty-lookup feedback contain no required graph action. Exact policy strings sent to each arm are saved in the raw report.

Both arms retain 12 data calls, 20 turns, 65536 context bytes, 1500 output tokens/request, two empty retries and two final repairs. Host feedback supplies used/max/remaining calls and actual exhaustion. Explicit false data-budget exhaustion statements are rejected with actual counts within existing repair limits; the narrow guard is not general semantic grading. No expected answer or evidence ID was injected, no graph disposition was overridden, and no extraction proposal was approved.

`COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests`: **201 passed in 58.16s**, including **13 actual-FalkorDB tests** (188 offline). Focused evaluator/budget suite: **69 passed**. Six new regressions check method-specific prompts/feedback, a supported search verdict derived from a returned record without graph assessment, and false exhaustion rejection, including the reviewed 10/12 case. The existing three-run actual-DB replay evidence remains [here](../live-corrections-2026-10-18/replay.json); it was not rerun for this policy-only change. Query, fixture, gold, authority and freshness code did not change.

## Raw measured outcomes

[Raw responses/tool traces/policies](live-openrouter.json), [unrounded counts and verified controls](counts.json), [API usage snapshot](openrouter-usage-reconciliation.json).

Same three affected cases, same order, same records/digests, scopes, dates, exact **openai/gpt-6-luna** model, OpenAI-only routing and numeric budgets as v4.1. No Claude or fallback. Both arms ran for every selected case; all **6/6 completed**. The report's global completed_with_failures also includes inherited raw-extraction rejections; extraction/narrative/smoke were not rerun and are not new measurements.

| Case | Graph | Search | Calls / remaining graph; search |
|---|---|---|---|
| clear | no_known_blockers; disposition/gaps correct | blocked; disposition/gaps wrong | 4 / 8; 12 / 0 |
| invoice owner/rationale | blocked; 8/8 required evidence, required workflow/blockers/owners/decision all correct | blocked; 6/8 evidence, 0/1 workflows, 1/2 blockers, 1/2 owners, 1/1 decision | 8 / 4; 12 / 0 |
| network slip/billing | blocked; 6/7 evidence, required workflow/blockers/owners/decision correct, one extra blocker | blocked; 6/7 evidence, required workflow/blockers/decision correct, 1/2 owners | 5 / 7; 12 / 0 |

Graph dispositions **3/3**, search **2/3**. All accepted finals have zero unsupported assertion IDs and valid assertion/source-key pairs under the local contract. This does not establish semantic correctness or completeness. Search ownership had one rejected final for treating invoice-export as a Workflow; the rejected content and corrected answer remain visible.

The introduced unavailable-action defect is verified absent from both saved search policy and live search behavior: search used only search_records/read_record and no final answer says assess_retirement is required or missing. Search clear-state independently reasons from its retrieved records and remains **wrong**: it treats an unchanged business requirement as a blocker despite replacement/clearance evidence and wants stronger direct service-level verification. That is a remaining model reasoning/coverage miss, not a successful clear-state result. Its call count is 12/12, unlike the false historical 10/12 exhaustion claim. Every accepted final's budget claims match host counts; no false-exhaustion rejection was needed in this live round.

Graph billing-slip reaches the actual FalkorDB assessment at the declared future planned_at and preserves blocked. It still omits **tracks-invoice-migration** from its final evidence list despite retrieving it: **6/7**, unchanged as a genuine citation-completeness miss. It also lists **legacy-runner** as an extra blocker outside the allowed blocker set. Neither was normalized away. No golden-driven completeness hint was added. The ownership graph answer satisfies the required structured fields; this is one known synthetic sample.

## Provenance, money and limits

The archived prior report matches the tracked v4.1 bytes exactly; SHA-256 is in counts.json. score_answer remains byte-identical to b5f87b4. Cohorts are separate; no pooling, denominator adjustment or replacement of historical scores occurred. Credential contents were held only in process memory, and exact-credential scans passed before copying evidence.

New round receipts: **USD 0.009913915**. Cumulative known receipts: **USD 0.047546820**. Read-only API key usage: **USD 0.048354995**, remaining **USD 2.951645005**, cap unchanged at **USD 3**. The new API usage delta exactly matches the round's receipts. The earlier **USD 0.000808175** aggregate/receipt difference is still unallocated, not an individually measured timeout cost. The full earlier timeout allowance **USD 0.00468431250** stays held; ledger accounted bound **USD 0.05223113250**, no open reservations and no halt. These overlapping figures must not be summed. No further inference is required for this report.

Equal numeric budgets do not mean equal work: graph returns consolidated policy/traversal results while search reads individual records. Schemas, host checks, source ranking, tool granularity, known-case debugging, single unseeded samples and model/network variation limit comparison fairness. This correction removes the identified impossible-action requirement; it does not establish general comparative superiority, isolate relationship traversal, validate production reliability or approve a later framework gate. No external MCP client UI session or relationship ablation was executed. Stage 7 remains under improvement for reasoning, role accuracy, citation completeness, unseen evaluation and human review. No research-branch change, push, publication, deployment, pull, merge or rebase occurred.

## Exact changed files since e4f8288

```text
README.md
docs/development/17-implementation-milestones.md
docs/development/18-local-development.md
evals/results/live-corrections-2026-10-18/README.md
evals/results/live-policy-2026-10-18/README.md
evals/results/live-policy-2026-10-18/counts.json
evals/results/live-policy-2026-10-18/live-openrouter.json
evals/results/live-policy-2026-10-18/openrouter-usage-reconciliation.json
evals/results/verification.md
src/company_brain/evaluation.py
src/company_brain/live_evaluation.py
src/company_brain/openrouter.py
tests/test_evaluation.py
```
