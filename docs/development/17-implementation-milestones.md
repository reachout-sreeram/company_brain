# Stage 7 implementation milestones

The governing framework is [the ten-stage engineering framework](../planning/10-engineering-framework.md). Stage 1 is concluded, Stage 2 principles remain, and the user selected Stage 3 service retirement readiness. The decision log explicitly allows the hackathon shortcut through formal Stages 4–6 with feasibility checks inside the first increment. The user's subsequent development authorization starts Stage 7; it does not establish Stage 8 acceptance or Stage 9 validation.

## Increment 1: evidence foundation

Implemented strict typed entity, source, assertion and inventory contracts, content hashes and exact source spans, scoped authority, immutable-source merges, explicit supersession, source revocation, deterministic fixtures, and an opt-in OpenRouter extraction adapter. Normal tests use seeded facts or explicitly labeled mock extraction. Trusted operator metadata supplies authority; models cannot grant it.

Verified: 64 evidence/ingestion and mocked-HTTP adapter tests passed. No provider calls were made. A real official FalkorDBLite 0.10.0 / FalkorDB 4.18.3 probe accepted parameterized Cypher and read-only queries. The sandbox blocks socket binding; the isolated runtime probe succeeded with approved execution permissions. Docker is absent.

Scope: foundational validation is executable. Quote equality is not semantic proof of an extracted claim. Operators must review extraction and compare against independent expected facts. Customer validation, broad connector ingestion, database scale and live extraction remain unverified.

## Review and gates

Each increment is committed locally with descriptive stage/test evidence. Existing planning edits are preserved outside these implementation commits. No pushes or history rewrites are authorized. The configured Git author email matches the authenticated `reachout-sreeram` account's public email.

Stage 7 remains in progress until the complete demo and its limits are reviewed. Stage 8 independent evaluation and Stage 9 real-world validation must not be marked complete from synthetic tests. Paid extraction requires a chosen model, spending limit, and secure credential setup before a live run.

## Increment 2: first complete retirement loop

Implemented FalkorDB assertion nodes and evidence edges, bounded graph queries, scoped deterministic resolution, conservative coverage, immutable revisions and compare-and-set publication, operator CLI, four read-only MCP tools, restart persistence, repeatable isolated reset/replay, and separate raw-source mock extraction into the actual graph. Added explicit target-service clearance and newer-observation requirements after review exposed unsafe clearance cases.

Verified: the final full suite at this milestone passed 88 tests (84 offline, 4 opt-in real FalkorDB integration), followed by 3 additional CLI guard tests. Three clean four-state replays produced identical canonical results. The raw-source CLI completed with `extraction_method: mock`. Actual MCP protocol round-trips and an ephemeral read-only database role were exercised. No live OpenRouter call or real Claude session occurred. See [local run instructions](18-local-development.md) and [the measured verification report](../../evals/results/verification.md).

Stage 7 now has a runnable first complete slice for human review. Stage 8 benchmark/independent scenario work and Stage 9 user validation remain open. No formal architecture or product validation is inferred from the hackathon shortcut or these tests.

## Increment 3: graph-native retrieval and review corrections

The independent review reproduced four false-clear/coverage defects; earlier passing tests did not establish correctness. Replaced application BFS and full revision JSON reads on the assessment path with scoped authorized row reads, Cypher temporal/supersession resolution and one bounded variable-length query returning complete dependency and migration-prerequisite paths. The actual query is in README. Added a derived current graph with semantic relation edges and assertion IDs; historical revisions and evidence remain separate. Publication switches current projection labels with the revision head.

Fixed extraction trust with operator-reviewed full-candidate digests, generic incomplete coverage for inaccessible evidence, same-target clearance renewal, and bounded response evidence with explicit truncation. Added decision ID and expiry to active dependency permissions, opt-in historical demo knowledge time, and provider-neutral client instructions. The previous Claude client choice is withdrawn. Live/paid providers remain unexecuted.

Verified on 17 October 2026: **101 tests passed in 33.96 seconds**, including **7 actual FalkorDB integration tests**; offline-only run: **94 passed, 7 skipped**. Three clean four-state real-DB replays matched every golden disposition and identical canonical results. An actual-DB test simulated wallclock +30 days: explicit demo configuration matched the fixed-time golden states and canonical outputs; unconfigured real freshness yielded `needs_verification`. Initial projection queries found Billing → Invoice export → legacy-runner and the blocker/owner path; migration removed the invoice legacy edge from current projection.

Socket startup first failed inside the sandbox. Supported elevated execution then permitted the isolated FalkorDB tests and replay. No denials were bypassed, no paid calls made, and no remote Git operation performed. Stage 7 remains under improvement; no later framework gate is self-approved. See corrected verification evidence below; older milestone timings are historical, not current measurements.

## Increment 4: evaluation preparation and same-graph questions

Added a provider-neutral model/tool harness with frozen equal model settings and budgets, scoped same-record iterative search/full reads, revision/dataset tracking, incomplete budget states and citation-support accounting. No new MCP tool or live inference adapter is exposed. Prepared manual narrative expectations, duplicate-aware TP/FP/FN scoring, and two additional golden answers using only the existing initial graph. The one-week slip answer distinguishes conditional retirement impact from an unsupported prediction of billing outage.

Raw preparation counts are reproducible with `.venv/bin/python -m company_brain.evaluation --prepare-only`: 4 input states; 2 question goldens requiring 15 evidence mentions; 3 narrative records with 2 expected facts; 1 existing deterministic mock record scored (1 TP, 0 FP, 0 FN); 2 narrative records without model output. Inference calls, provider requests, live benchmark runs and real-client transcripts are all zero. Mock scoring is a contract check, not measured model quality.

The expanded full suite passed **110 tests in 35.80s** (102 offline + 8 actual FalkorDB integration). The new real-DB test supports both extra question goldens and a clearly labeled scripted comparison-harness probe; it does not simulate a real-client transcript. The existing official MCP protocol test now also pins demo time, checks instructions against disposition override, and rejects timezone-naive dates. A targeted rerun verifies these added protocol assertions. See [evaluation preparation](../../evals/results/evaluation-preparation.md) and [submission plan](19-submission-plan.md).

No live benchmark, real extraction, relationship ablation, push, visibility change or deployment occurred. Later framework gates remain open. Publishing authorization and paid model/cap/secure-setup gates remain pending.

### Final review follow-up

Tightened partial-response consistency: when the evidence budget omits supporting citations, remove nested permission references and workflow findings whose paths were omitted. Added checks across budgets 1/4/8/12 and an actual-DB bounded-response check. Full suite: **110 passed in 39.91s**. Final offline run after the evaluator correction: **102 passed, 8 skipped in 0.35s**.

The generated mock-narrative report exposed a scorer default-normalization defect (`supersedes` omitted versus `[]`); fixed it, added a regression, and regenerated the raw report. The available permission mock now scores 1 TP / 0 FP / 0 FN; this remains a curated deterministic mock, never live extraction accuracy. Earlier intermediate mock counts were not valid evaluation evidence. No framework gate has been closed.

## Independent rereview correction: search metadata privacy

The rereview found that baseline `read_record` copied inventory declarations containing inaccessible consumer IDs even though MCP assessment hid those identities. Search now omits the entire inventory declaration if its target service or any declared consumer is inaccessible, reports generic incomplete coverage, and returns no original consumer count. It also filters inaccessible predecessor assertion IDs from supersession metadata to match MCP history. Authorized callers still receive the full permitted declarations and references. Public source text retains the same source-level access as MCP evidence.

Three new privacy regressions initially failed, then passed after the fix. Verification: 105 offline tests passed, 9 actual-DB tests skipped in the offline run (0.37s). Two actual-DB checks passed in 8.16s: the independent inventory reproducer plus a repository regression covering both hidden consumers and hidden target services. This is a correctness correction, not Stage 8 acceptance. Supersession-chain rereview work remains in progress.

## Independent rereview correction: transitive temporal supersession

The rereview reproduced a valid clearance renewal chain that resurrected an old reporting dependency because the intermediate clearance had expired. Resolution now follows bounded transitive supersession in actual Cypher. The descendant and candidate must be currently eligible. Intermediate expiry alone does not break historical lineage, but every member must remain approved, same-subject/scoped/revision, visible, nonrevoked and available at the requested knowledge cutoff. Invalid scope/subject/target supersession remains rejected. Ingestion enforces the same 16-link limit as the query; longer chains fail before publication.

Added 17 offline renewal/temporal/privacy regressions and three actual-DB matrix tests. They cover 2-, 3- and 16-hop chains; earlier known-at and business intervals; expired clearance without renewal; a historical gap; revoked/restricted/future endpoints and intermediates; authorized/public differences; immutable earlier revisions after revocation; and invalid scope/depth preserving the published head. No Python traversal was added to production; Python enumeration remains an explicitly named test double only.

Combined final command `COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests /tmp/test_company_brain_rereview_db.py` passed **137 tests in 64.49s**: 122 offline + 12 repository actual-FalkorDB tests + 3 independent actual-DB reproducer tests. The independent renewal/privacy reproducers now pass, and its three clean replays retain 12/12 golden dispositions with identical canonical results. README and the standalone `.cypher` artifact reproduce the full updated query. Stage 7 remains under improvement, with no later framework acceptance inferred.


## Authorized live synthetic round — 18 October 2026

The user approved exact OpenRouter model `openai/gpt-6-luna`, USD 3 total, and process-memory use of the existing ignored project credential. Implemented native API function calls with actual role=tool messages, matched graph/search controls, contextual raw-source extraction and a durable cross-attempt spending ledger. Removed an unsupported parallel_tool_calls parameter after the router rejected it; no Claude fallback was used. Earlier protocol failures and one timeout are preserved, not pooled into the latest cohort.

The latest paired cohort terminated all 12 arms: graph completed 6/6, search completed 3/6 and exhausted its equal tool budget in three. Graph matched all four retirement dispositions but had two citation-ID format errors; it failed the network-slip question after an unsuccessful broad entity lookup. Search's completed clear-state answer was conservative but wrong, and its extra question outputs failed structured fields/citation contracts. Narrative raw counts: 2 TP / 0 FP / 0 FN across three known synthetic records. Raw extraction: 13 records, 11 validations, two undated dependencies rejected, nine proposals, zero approved; actual raw graph remains needs_verification. These are exploratory results, not comparative performance, general model quality or human acceptance.

Full repository run passed 168 tests in 54.64s, including 12 actual-FalkorDB integration tests. Three fresh isolated real-DB replays passed 12/12 golden dispositions with identical canonical outputs. Then a report-only archive/resume correction added one test: final offline suite 157 passed, 12 integration skipped in 0.19s; focused budget suite 27 passed. It preserves old reports and removes inherited error/status from future resumed cohorts. The historical current raw artifact retains its stale top-level error, explicitly documented rather than rewritten.

Cumulative known receipts USD 0.021924765; one unresolved timeout retains USD 0.00468431250 allowance (ledger accounted USD 0.02660907750). Final read-only key usage USD 0.02273294, remaining USD 2.97726706, unchanged USD 3 limit. These overlapping figures must not be summed. See [full raw evidence and limits](../../evals/results/live-2026-10-18/README.md). Stage 7 remains under improvement: retrieval robustness, exact answer/citation contracts, raw proposal approval, broader unseen scenarios and provider-neutral external MCP client validation remain open. No subsequent framework gate, publication, push or deployment is approved.

## Retrieval and citation-contract correction

User-requested correction on dev: one-entity discovery guidance, bounded lexical retry feedback after empty entity/record searches, and rejection of premature empty-lookup finalization. Final schema separates exact assertion IDs from assertion/source-key pairs and describes exact workflow/decision IDs. Local validation checks only actually retrieved references plus authorized entity types, ownership support, coverage-gap presence and the retrieved assessment disposition. Both arms receive the same two final-repair turns inside unchanged shared budgets; invalid attempts and typed errors remain in the trace. Original v3 scores and raw attempts remain unchanged.

Focused checks: 59 passed. Full command `COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests`: **191 passed in 57.93s** (178 offline + 13 actual-FalkorDB tests). A scripted reproduction rejects premature finalization after the combined phrase misses, resolves a shorter term, follows returned IDs and reaches actual Cypher assessment; it contains no production golden-answer shortcut. Three clean four-state replays: **12/12 dispositions**, identical canonical outputs. The next measured action is a separate affected-case paired live rerun; no quality improvement is inferred yet. Stage 7 remains open.

### Follow-up after the first corrected live cohort

The v4 affected-case rerun improved graph clear-state citations and ownership structured fields, but billing-slip still exhausted 12 calls on rediscovery and optional histories before assessment. All three baseline arms exhausted their call budgets. Preserve this run separately; it is not a successful billing fix. Added shared numeric budget disclosure and remaining-call metadata, direct reuse of returned IDs/source keys, omission of guessed entity kinds and assessment before optional exploration once a service is known. Repeated identical empty lookups now consume retry allowance too; four new regressions failed before this follow-up and pass afterward.

Focused tests: **63 passed**. Full offline + actual-FalkorDB suite: **195 passed in 59.17s**, including **13 real-DB tests**. No graph query, fixture, freshness rule, authority approval, gold answer, output token cap or tool budget changed. A separate v4.1 paired rerun will measure these changes rather than pool results with v3/v4. Framework gates remain open.

### Measured correction outcome

The v4.1 affected-case paired round completed 6/6 arms. Graph dispositions match 3/3; search 2/3, with clear-state still conservative but wrong. All accepted finals contain exact supported assertion/source pairs and zero unsupported assertion IDs. Ownership graph output matches all required structured fields and 8/8 evidence. Billing-slip now resolves billing and reaches actual-FalkorDB assess_retirement at the correct planned time; it preserves blocked, both owners, workflow, blockers and exception decision, but cites only 6/7 required evidence IDs (tracks-invoice-migration omitted). Search still lacks required details. One search final was rejected for wrong Workflow type and unsupported owner pair, then corrected; original rejected content remains in the trace.

[Separate v4/v4.1 raw evidence, strict counts, costs and limitations](../../evals/results/live-corrections-2026-10-18/README.md) retain the unsuccessful intermediate cohort and unchanged v3 baseline. Cumulative known receipts USD 0.037632905; two correction rounds USD 0.015708140. Final read-only API snapshot USD 0.03844108, unchanged USD 3 cap; new settled usage delta exactly matches the correction receipts. Prior unallocated cost is not individually attributed, and the earlier USD 0.00468431250 timeout allowance remains held (ledger accounted USD 0.04231721750). No additional paid call is needed for the report. Stage 7 remains open for citation/answer completeness, unseen evaluation and human acceptance; no public action or research-branch integration occurred.
