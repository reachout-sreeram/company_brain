# Final Stage 7 implementation handoff — 18 October 2026

Tested core **985f0c7**, following fidelity **c87253d** and explicit approval **485d71c**. This freezes the measured local implementation for user review, release and recording. It does **not** self-approve Stage 7 or later human gates.

## What changed

Graph answers now preserve all returned assessment workflows, blockers, owners and decision IDs, cite every evidence row in the scoped packet and cannot add a blocker. Record-derived answers need cited support for the role they claim; mentioning a dependency target does not establish it as a blocker. Rejected attempts remain in traces and use the existing bounded repair budget; neither gold answers nor unreturned evidence are supplied. The deterministic graph disposition stays authoritative.

`approve-proposals` requires explicit selected IDs, actor, time, note and fresh output file. It retains original proposals/sources, creates approved copies and immutable audit selections with full-claim digests, and publishes them through the existing operator ingest path. Real FalkorDB stores review nodes with APPROVES/REVIEWED_FROM edges. Approval knowledge time is filtered in native Cypher, so a later review cannot rewrite an earlier knowledge view. Evidence labels approval_kind demonstration/operator. Operator identity is a trusted local input, not production authentication. No MCP write tool exists.

REQUIRES supports explicitly declared business validity separately from observed runtime usage. Only source text dates or requires_valid_from/until metadata can establish that interval; missing times never become now. RUNS_ON, DEPENDS_ON and observed REQUIRES retain explicit observations and seven-day freshness. Runtime verification cannot be replaced by a timeless contract. Source/approval knowledge, scope, interval, revocation and visibility remain required. The two raw prerequisite records are version 2 with declared synthetic validity metadata and unchanged narrative text; structured four-state fixtures and goldens remain unchanged. [Detailed review semantics](../../../docs/development/proposal-review.md).

## Verification

- `COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests`: **229 passed in 68.31s**, including **15 actual-FalkorDB tests** (214 offline). The earlier full attempt had 226 passes and one incorrect new test expectation: stale runtime does not erase independent open migration prerequisites. Its corrected test explicitly preserves blocked while asserting all runtime paths stale; targeted actual-DB checks and this final complete suite pass. No production rule was weakened for that correction.
- Three clean post-query-change real-DB resets/replays: **3/3 runs, 12/12 golden dispositions**, identical canonical outputs; `[blocked, blocked, needs_verification, no_known_blockers]`. [Raw replay](replay.json).
- Separate portable MCP client contract tests: **9 passed**. A fresh zero-API SDK stdio run on the current schema passed all four tools, 13 exact source-span checks, same-revision pinning and naive-time rejection. [Current-schema protocol evidence](../../../presentation-assets/mcp-client-demo/current-schema/protocol-transcript.json).
- Separate live Luna → SDK → MCP stdio → actual FalkorDB client passed its final strict contract, preserved verdict/gaps/conflicts/permission expiry and matched 13 assessment citations. One exception span was independently inspected. Its earlier expiry-field-name failure and other attempts remain preserved. This is a CLI model agent, not a desktop UI/video. [Client report](../../../presentation-assets/mcp-client-demo/LUNA-DEMO.md).
- Actual operator CLI proof: recorded proposals remained inactive, four explicitly selected/source-checked demonstration approvals changed needs_verification to blocked, and the prior knowledge cutoff remained needs_verification. Seven proposals were retained unapproved. [Exact commands and source/candidate IDs](../../../presentation-assets/reviewed-demo/README.md); [raw before/after/audit](../../../presentation-assets/reviewed-demo/recorded-proof/proof.json). The portable replay wrapper also passed a second isolated real-DB handoff check without a paid call.

## Full live cohort

[Raw responses, tool traces, rejected finals and policies](live-openrouter.json), [unrounded counts and proof summary](counts.json), [read-only account usage](openrouter-usage-reconciliation.json).

Exact model **openai/gpt-6-luna**, OpenAI provider only, no fallback; reasoning none, unsupported temperature omitted. Same record set/digest per paired case, production/eu scope, declared planned_at/known_at. Limits: 1500 output tokens/request, 20 turns, 12 data-tool calls, 65536 serialized context bytes, two empty-query retries and two final repairs. The source schema now includes approval/time-basis metadata; do not treat this as byte-identical data encoding to historical cohorts. Within this round the two methods receive the same records. Smoke, all raw records, narrative cases and all six paired cases were actually executed again. All 124 inference responses have cost receipts.

| Case | Graph disposition | Search disposition | Graph/search calls |
|---|---|---|---|
| initial | blocked — correct | blocked — correct | 2 / 12 |
| completion | blocked — correct | blocked — correct, required workflow omitted | 2 / 12 |
| migration | needs_verification — correct | blocked — wrong | 4 / 12 |
| clear | no_known_blockers — correct | blocked — wrong | 2 / 12 |
| invoice owner/rationale | blocked — correct; 8/8 required evidence | blocked — correct; 6/8 required evidence | 5 / 11 |
| network slip/billing | blocked — correct; 7/7 required evidence | blocked — correct; 4/7 required evidence | 6 / 11 |

All **12/12 arms completed**, graph dispositions **6/6**, search **4/6**. Both extra graph answers match required workflows, owners, blockers and decision IDs, have **no extra workflows/blockers**, and cite all required evidence; every accepted final has zero unsupported assertion IDs. This is reference/field validity, not a general proof of every sentence. Initial/completion search and both ownership answers plus graph billing-slip needed one bounded final correction each (five rejected finals total). Raw rejected content remains visible. Graph ownership/billing fixes came from general returned-packet fidelity, not golden-specific prompts or altered scoring. score_answer is unchanged from b5f87b4.

These are repeatedly debugged, single samples on known synthetic cases. Graph includes consolidated deterministic policy and fidelity checks, while search reads individual records and derives policy. Tool granularity, schemas, host assistance, ranking, context overhead and model variation constrain fairness. There is no ablation, unseen-set claim, significance test, scale benchmark, general superiority or database-speed claim. Historical cohorts, including v4.1's introduced unavailable-action confound, are retained separately and are not pooled into these denominators.

## Raw extraction and review limits

All **13 raw records validated**, yielding **11 proposals, 0 automatic approvals**. The two prerequisite records now extract declared validity without invented observed_at. The migration-tracking record yielded no claim; inventory yields no assertion. Schema/span validation is not fact accuracy.

Three separately scored narrative records: **2 expected facts, 2 proposals, 1 TP / 1 FP / 1 FN**. Permission is correct; injection emits no facts. The completion claim's subject/predicate/value are right but its effective_from incorrectly falls back to recorded time 17 October instead of the stated as-of time 16 October. The strict scorer retains the mismatch. That separate narrative-evaluation candidate is outside the 13-record initial proposal bundle; it was neither ingested nor approved. This remains a model semantic-date limitation, not a successful general extraction result.

The demonstration selected only runtime, billing prerequisite, export owner and dated permission after inspecting full source text and metadata. It did not approve all live output, invent the omitted migration link, make a real-human approval claim or yield retirement clearance. The review CLI is additive and does not infer supersession links; distributed/authenticated production reviewer identity is outside scope. Existing source authority and validation still apply after review.

## Budget reconciliation

Final full round: **USD 0.021175760**, summed from 124 response receipts. Separate MCP worker: **USD 0.004000040 total**, reconciled once (USD 0.002270205 plus USD 0.001729835); unused USD 0.095999960 allocation released. Cumulative known receipts: **USD 0.072722620**. API settled usage: **USD 0.073530795**, remaining **USD 2.926469205**, unchanged cap **USD 3**. Since the prior API snapshot, the usage increase exactly equals the full-round receipts plus the worker total.

The older **USD 0.000808175** aggregate/receipt difference remains unallocated, not asserted as an individually measured timeout cost. The prior conservative timeout allowance **USD 0.00468431250** remains held; accounted ledger bound **USD 0.07740693250**. Overlapping API, receipt and allowance figures are not summed. No open reservation, halted ledger, active inference process, top-up, limit increase or further inference request remains.

## Freeze and handoff

README now integrates the judges draft with the actual query, tested approval scene and truthful client/results labels. [Three-minute script](../../../docs/development/demo-3min.md) and portable assets are provided for user-owned recording. The official rules/schedule checklist remains pending for visibility, registration, track confirmation, video and submission receipt; no push, visibility change, submission, deployment, desktop configuration or recording was performed here. No remote research/Deblina history was integrated. Stage 7 remains under improvement/human acceptance with known model semantic-date and search completeness/reasoning limits.
