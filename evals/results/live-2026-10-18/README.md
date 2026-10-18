# Authorized Luna synthetic evaluation — 18 October 2026

This is a small exploratory execution, not a benchmark advantage or framework acceptance. The user authorized `openai/gpt-6-luna` through OpenRouter, the existing ignored project credential and a **USD 3 total cap**. No Claude model, external MCP client UI, push, publication or deployment was used. Native API responses report the standard Luna dated alias. Credentials were read into process memory only; the six copied raw artifacts were scanned for the exact credential before inclusion.

## Evidence and protocol history

- [Latest raw run](live-openrouter.json): native function calls, actual role=tool replies and original API call IDs; all 12 comparison arms terminated. **Its inherited top-level error is stale from attempt3**, not a current stop. Arm outcomes and completed_with_failures status describe this completed cohort. Original bytes are retained; the runner now archives old reports and clears stale status/errors on resume, covered by a regression.
- [Raw counts](counts.json): unrounded metrics, controls and cumulative cost summary.
- [Attempt1](live-openrouter-attempt1.json): earlier JSON-action protocol finished, but all 12 arms produced malformed output. Not pooled with the native cohort.
- [Attempt2](live-openrouter-attempt2.json): strict JSON-action retry, including three budget/format failures and a timeout; incomplete, not pooled.
- [Attempt3](live-openrouter-attempt3.json): improved raw extraction and narrative, then native routing rejection for an unsupported parallel_tool_calls parameter. Retained extraction/narrative in the latest run; comparison alone was resumed after removing that parameter. No silent paid retry.
- [Read-only account reconciliation](openrouter-usage-reconciliation.json) and [three deterministic real-DB replays](replay.json).

## Frozen comparison controls and limitations

Six cases, one sample per arm, counterbalanced order; identical model, per-case record digest/revision, production/eu scope, declared planned_at/known_at, and same original source records/validated assertions. Native API tools were supplied on each turn. Limits: 1500 output tokens/request, reasoning effort none, temperature omitted because unsupported, 20 turns, 12 tool calls, 65536 serialized context bytes; one OpenAI provider with no fallback. Graph arm uses the four existing read-only tools. Search uses iterative search_records/read_record over the same accessible records; neither receives gold answers. finish_answer is an internal API answer carrier, not an added MCP tool. Actual FalkorDBLite stores both seeded comparison states and the separate raw extraction graph.

Equal tool budgets do not establish equal work: assessment returns a consolidated result, whereas baseline reads individual records. Search ranking, tool descriptions, host policies and single-sample model variation materially affect results. Recorded context_bytes are harness serialization sizes, not provider token counts; native wire size is checked separately. Latency includes live inference/tools on one Mac/network, with no repeated samples or cache control. The graph arm receives deterministic policy computation; this comparison does not isolate relationship traversal. No relationship ablation was executed.

| Case | Graph status / disposition | Search status / disposition | Graph/search tool calls |
|---|---|---|---|
| initial | completed / blocked | tool budget exhausted | 2 / 12 |
| completion | completed / blocked | tool budget exhausted | 4 / 12 |
| migration | completed / needs_verification | tool budget exhausted | 2 / 12 |
| clear | completed / no_known_blockers | completed / needs_verification | 4 / 10 |
| invoice owner/rationale | completed / blocked | completed / blocked | 8 / 11 |
| network slip/billing | completed / needs_verification | completed / blocked | 1 / 9 |

All four graph retirement-state dispositions match gold; the sole completed search retirement-state answer does not. Three search arms have **no final answer**, not scored as correct. Across all six cases, graph dispositions match 5/6; search matches 2/6, with 3 incomplete and 1 wrong. These are raw outcomes under these controls, not evidence of general superiority.

The strict assertion-ID citation checker counts **2 unsupported IDs in graph clear**, and **1 in search network-slip**. Manual inspection: graph cited source-key-plus-assertion strings (`source-clear-report@1#clear-report`, `source-run-invoice-v2@1#run-invoice-v2`) for actually retrieved facts instead of the required assertion IDs. Search cited `inventory-initial`, an inventory record rather than an assertion. The original checker and failures are preserved; do not equate these format/type errors with invented underlying facts or silently count them as supported. Other completed arms had zero unsupported assertion IDs under this narrow checker; it does not prove every natural-language statement correct.

For invoice ownership/rationale, graph retrieved all 8 required evidence IDs and both owners, but matched only 1/2 required blocker entities and 0/1 exact decision IDs. Search matched 5/8 evidence IDs, both owners, 1/2 blockers and 0/1 exact decision IDs, with a workflow-ID mismatch. Decision prose contains the exception but does not satisfy the exact-ID output contract. On network-slip, graph searched the combined phrase “billing network approval”, received no entity candidates and stopped with needs_verification: 0/7 evidence, no owners/workflow/blockers, wrong disposition. Search matched 5/7 evidence, both owners, 1/2 blockers, but workflow-ID and decision-ID contracts failed, plus the inventory citation error. Full answers remain in raw evidence.

## Same-graph expected answers

Invoice export belongs to **data-platform** (`owns-invoice`). Its observed configuration is legacy-runner (`run-invoice-legacy`); invoice-migration is open and blocked by open network-approval, owned by security (`tracks-invoice-migration`, `status-migration-open`, `blocked-network`, `status-network-open`, `owns-network`). Decision **temporary-exception** permits continued use until **2026-11-01T00:00:00Z** (`permits-invoice`); permission is not runtime clearance. The live graph answer explains this chain but still fails some strict structured fields above.

Billing requires invoice export, which is observed on legacy-runner (`requires-billing-invoice`, `run-invoice-legacy`). If network approval slips one week, the migration prerequisite remains unresolved; retiring the runner while that dependency remains risks billing. Records do **not** establish an inevitable outage, exact lost billing runs, future completion, or an approval due date. Reverify at the future time; the exception is finite and reporting coverage remains stale. The live graph model failed this question; this expected answer comes from the pre-existing golden, not a successful live transcript.

## Raw extraction and narrative

13 raw source records: **11 schema/semantic validations, 2 rejected records** for absent explicit dependency observation time. Nine candidate assertions remain **9 proposals, 0 approved** because actual candidate digests differ from the previously reviewed mock digests. Report-job yielded no claim; inventory yielded no assertion. This is not 11/13 fact accuracy. The actual raw graph assessment returns needs_verification, no retirement clearance. No source timestamp was substituted for missing runtime observation, and no approval was fabricated to improve the demo.

Three separately scored narrative records: **2 expected facts, 2 proposals, 2 TP, 0 FP, 0 FN**. Permission and completion are represented; injection produces zero claims. This tiny known synthetic set is not general extraction quality or an unseen benchmark.

## Money and verification

Cumulative known response receipts: **USD 0.021924765**. One earlier timeout has no generation ID; retain **USD 0.00468431250** conservative allowance, giving ledger-accounted **USD 0.02660907750**. Read-only key usage after completion: **USD 0.02273294**, remaining **USD 2.97726706**, limit unchanged at **USD 3**. Aggregate usage is not individually attributable timeout cost; do not add it to receipts. The earlier pre-provider routing rejection was reconciled to zero only after usage delta matched successful receipts. No top-up or limit change occurred. No further inference is needed for this report.

Before the report-only runner correction: full repository suite **168 passed in 54.64s**, including **12 actual-FalkorDB integration tests**. Final offline suite after the archive/resume regression: **157 passed, 12 integration skipped in 0.19s**; focused budget tests **27 passed**. Three fresh isolated actual-FalkorDB resets/replays: **3/3 runs and 12/12 golden dispositions**, canonical outputs identical, states blocked → blocked → needs_verification → no_known_blockers. Prior real-DB +30-day configured-demo test retains freshness protection. Test success does not erase the live answer failures.

Stage 7 remains under improvement. Entity retrieval robustness, exact citation/decision contracts, raw proposal review, broader unseen evaluation, external provider-neutral MCP client validation, and human framework acceptance remain open. No Stage 8/9 gate is self-approved. Publication still requires later user authorization.
