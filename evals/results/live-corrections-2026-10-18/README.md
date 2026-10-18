# Retrieval and exact-reference corrections — 18 October 2026

The requested defects are corrected in the harness and measured separately from the [original v3 results](../live-2026-10-18/README.md). This is a small, known synthetic evaluation, not a benchmark advantage, external MCP client validation, or framework acceptance.

## Changes and evidence

- `363758f`: single-entity discovery guidance; bounded empty-result decomposition and premature-final rejection; exact assertion/source-reference schema; local reference/type/ownership/disposition checks; equal bounded final-repair turns for both arms; scripted and actual-FalkorDB regressions.
- `c480bea`: shared initial/remaining numeric budget disclosure; direct reuse of returned IDs/source keys; omit guessed kind filters and assess as soon as a service is identified; repeated identical empty misses consume retry allowance.
- [Raw v4 first corrected cohort](live-openrouter-archive-2.json), [raw v4.1 follow-up](live-openrouter.json), [unrounded counts and controls](counts.json), [replays](replay.json), [read-only key usage snapshot](openrouter-usage-reconciliation.json).

The v3 archive bytes match the tracked original SHA-256 recorded in counts.json. Original strict scoring functions are byte-identical to b5f87b4; no gold, source fixture, authority rule, Cypher query, freshness rule or MCP tool was changed. All rejected finals and typed local errors remain visible in final_attempts. Smoke, narrative and raw extraction in the new report are inherited evidence, not rerun measurements. Extraction proposals remain unapproved.

The first corrected v4 round completed graph clear-state and ownership with exact citations, but graph billing-slip spent 12 calls on rediscovery and optional histories before reaching assessment. All three search arms exhausted the call budget. Those failures are preserved, not pooled with or replaced by v4.1. Four follow-up regressions reproduced absent budget disclosure and identical-query retry counting before the correction.

## Latest v4.1 outcomes

Same three cases, both arms, same model and dataset digests/revisions. All **6/6 arms completed** within the unchanged tool budgets. No accepted final had an unsupported assertion ID or invalid assertion/source-key pair.

| Case | Graph | Search | Data calls graph/search |
|---|---|---|---|
| clear | no_known_blockers; disposition/gaps correct, 0 unsupported IDs | needs_verification; disposition/gaps wrong, 0 unsupported IDs | 5 / 10 |
| invoice owner/rationale | blocked; all required structured fields, 8/8 evidence, 0 unsupported IDs | blocked; 4/8 evidence, 0/1 workflows, 1/2 blockers, 1/2 owners, 0/1 decisions | 5 / 12 |
| network slip/billing | blocked; correct workflow, blockers, owners and decision; 6/7 evidence, 0 unsupported IDs | blocked; 3/7 evidence, correct workflow, 1/2 blockers plus one extra, 0/2 owners, 0/1 decisions | 7 / 10 |

Graph dispositions match **3/3**, search **2/3**. These are single samples on a selected known set after debugging, not unbiased accuracy estimates. The original six-case v3 cohort remains the original exploratory result. Do not combine cohorts to claim a larger sample or general improvement rate.

Billing-slip now starts with `find_entities(query="billing", kind=null)`, resolves monthly-billing, follows returned requirement/configuration evidence and invokes **assess_retirement on legacy-runner in production/eu with planned_at 2026-10-24T12:00:00+00:00**. The assessment runs the existing native Cypher on actual FalkorDB and returns blocked. The model preserves that disposition. It explains conditional migration/billing risk, finite permission through 1 November and incomplete reporting coverage without predicting an inevitable outage or successful future work. It **omits tracks-invoice-migration from the final citation list**, despite retrieving it; 6/7 remains a recorded completeness miss.

Invoice ownership now returns exact `data-platform` and `security` owner pairs, `monthly-billing` workflow, active dependency `invoice-export`, blocker `network-approval`, and decision ID `temporary-exception`, with all 8 required evidence IDs. Clear-state uses exact assertion IDs and separate source references. In v3, its composite source#assertion strings referred to retrieved facts: the old score of 2 unsupported IDs remains, with the manual classification **citation-format error**, not invented underlying facts.

Search ownership used one local repair: the validator rejected invoice-export in the Workflow field and a network-approval/security owner pair that had not been substantiated by a returned ownership record. The model removed those unsupported fields and reported gaps; the rejected answer remains in the trace. No missing golden item was supplied by the validator. Local checks establish reference validity and selected contract invariants, not complete or semantically correct answers. Search's conservative clear-state answer is still wrong against the full-record golden; no verdict was overridden to improve its score.

## Controls and limits

Exact model **openai/gpt-6-luna**, OpenAI provider only, no fallback, reasoning effort none, temperature omitted, 1500 output tokens per request, 20 total turns, **12 data-tool calls**, 65536 serialized context bytes, at most **2 empty-lookup retries and 2 final-repair turns** per arm. Repairs consume turn/context/money budgets, not additional data-tool allowance. Initial budgets and remaining-call metadata are supplied to both arms. Both have the same applicable exact-ID/source-pair/ownership checks; graph additionally must preserve any retrieved assessment disposition. Native tool_calls and role=tool responses retain original API call IDs. finish_answer remains an internal answer carrier, not a new MCP tool.

Lexical retry hints use only the failed query, never catalog search or gold answers. An exact entity ID must occur in a structured returned result before final acceptance. Authorized catalog kinds support host type checking only; no unseen facts or paths are supplied. Assertion/source pairs and ownership must be backed by returned structured evidence. Exhaustion or unresolved invalid output is incomplete, not a successful answer. MCP instructions also recommend single-entity lookup and bounded retries; the server still exposes only the four existing read-only tools.

Equal calls are not equal work: graph assessment consolidates deterministic policy and traversal, while search reads individual records. Search ranking, tool granularity, repeated model calls, host assistance, schemas, context overhead, sample variation and known-case debugging constrain fairness. No relationship ablation or repeated-sample significance test was run. These results do not isolate graph traversal, establish production reliability, or prove FalkorDB speed superiority. Context_bytes are harness serialization counts; native wire size is separately bounded. Latency includes model/network/tool time on one Mac without cache control.

## Verification and money

`COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests`: **195 passed in 59.17s**, including **13 actual-FalkorDB tests**. Focused evaluator/budget suite: **63 passed**. The earlier correction checkpoint passed 191 tests in 57.93s. Three clean actual-DB resets/replays: **3/3 runs, 12/12 golden dispositions**, identical canonical outputs. Replay command and raw output are retained; query/fixture/freshness code did not change during the harness-only follow-up.

Cumulative known inference receipts: **USD 0.037632905**. v4 increment: **USD 0.007485295**; v4.1 increment: **USD 0.008222845**. Both correction rounds together: **USD 0.015708140**. One earlier unresolved timeout still retains **USD 0.00468431250** allowance; ledger accounted upper bound is **USD 0.04231721750**, no reservations remain open, and the ledger is not halted. The API key limit remains **USD 3**. Key usage is an asynchronously settling aggregate snapshot, preserved separately; do not add it to receipts or use it to discard the unresolved timeout allowance. No limit change, top-up, model switch or additional extraction approval occurred.

Stage 7 remains under improvement. The remaining observed gaps are citation completeness and search answer completeness/clear-state accuracy, followed by broader unseen evaluation and human review. No subsequent framework gate is self-approved. No Claude, pull, rebase, merge, push, publication, visibility change or deployment occurred; research remains untouched at e5a6321 while corrections are committed on dev.

Final settlement check: API usage **USD 0.03844108**, remaining **USD 2.96155892**, cap still **USD 3**. Its increase from the pre-correction snapshot (USD 0.02273294) is exactly **USD 0.015708140**, matching both correction rounds' receipts. The earlier read immediately after completion lagged at USD 0.03609128; [that first snapshot](usage-initial-snapshot.json) is preserved separately. The prior USD 0.000808175 difference between aggregate usage and known receipts remains unallocated, not asserted as an individually measured timeout cost; the full timeout allowance stays held.

## Exact changed files since b5f87b4

```text
README.md
docs/development/17-implementation-milestones.md
docs/development/18-local-development.md
evals/results/live-corrections-2026-10-18/README.md
evals/results/live-corrections-2026-10-18/counts.json
evals/results/live-corrections-2026-10-18/live-openrouter-archive-2.json
evals/results/live-corrections-2026-10-18/live-openrouter.json
evals/results/live-corrections-2026-10-18/openrouter-usage-reconciliation.json
evals/results/live-corrections-2026-10-18/replay.json
evals/results/live-corrections-2026-10-18/usage-initial-snapshot.json
evals/results/verification.md
src/company_brain/evaluation.py
src/company_brain/live_evaluation.py
src/company_brain/openrouter.py
src/company_brain/server.py
tests/test_evaluation.py
tests/test_integration.py
tests/test_openrouter_budget.py
```
