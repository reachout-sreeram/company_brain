# Stage 7 functional verification — 17 October 2026

Backend: real FalkorDB 4.18.3 through official FalkorDBLite 0.10.0, client 1.8.0. Platform: macOS-26.5.2-arm64-arm-64bit-Mach-O, Python 3.13.11. No live model/API calls.

Tests: the integration-enabled suite passed **88 tests in 21.14 seconds**, followed by **3 additional CLI guard tests in 0.13 seconds**.

The three clean replays each matched all four manually declared golden dispositions and identical canonical evidence-linked results:

| Fixture | Result | Explanation |
| --- | --- | --- |
| initial | blocked | Billing still depends on invoice export on the legacy runner; network approval blocks migration; reporting evidence is stale |
| completion | blocked | Ticket completion conflicts with newer usage; dependency remains |
| migration | needs_verification | Verified scoped migration removes billing impact; stale reporting coverage remains |
| clear | no_known_blockers | Fresh target-scoped reporting verification completes the declared inventory; human shutdown approval is still required |

Final logical revision: 11 entities, 20 immutable source versions, 17 assertions, 1 declared inventory. The store also retains prior revisions and graph representations; this is a tiny demo graph.

Measured 12 direct assessments across three resets: min 1.078 ms, max 3.422 ms, nearest-rank p95 3.422 ms. Reset times: 0.398, 0.301, 0.279 ms. These are local in-process measurements after ingestion, with engine defaults and no cache flush. They exclude client intent interpretation and answer generation. They do not establish the MCP p95 target or a speed advantage over another database.

Real integration verifies parameterized graph traversal, immutable history, idempotent ingestion, failed-publication preservation, restart persistence, the four tools through an official MCP client/server protocol session, and ephemeral graph-reader ACL denial of mutations. Raw-source mock extraction was separately run through the installed CLI and actual graph; its method is explicitly `mock`.

Commands:

```sh
COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q
COMPANY_BRAIN_LITE_PATH=/tmp/company-brain-stage7-demo.rdb COMPANY_BRAIN_GRAPH=company_brain_demo_evaluation .venv/bin/python -m company_brain.replay --confirm-graph company_brain_demo_evaluation --replays 3
COMPANY_BRAIN_LITE_PATH=/tmp/company-brain-stage7-raw.rdb COMPANY_BRAIN_GRAPH=company_brain_demo_raw_cli .venv/bin/company-brain extract-ingest data/raw_demo/manifest.json --mock-candidates data/raw_demo/mock_candidates.json
```

Generated detailed output: `evals/results/replay.json` (local, intentionally ignored), including every assertion/source/span used. The replay can regenerate it. Golden inputs remain separate from query tools.

Limits: no real Claude Desktop session, paid OpenRouter extraction, search-only baseline, relationship ablation, production identity deployment, broad connector ingestion, production-scale testing, or real-user validation. Functional tests do not close framework Stages 8 or 9. No persistent credentials, pushes, deployment, real company uploads, or global Git configuration changes occurred.

## Correction increment — 17 October 2026 (supersedes earlier correctness claims)

Independent review reproduced wrong-subject extraction activation, missing restricted-coverage warnings, rejected valid clearance renewal, and evidence-budget overflow. All four now have dedicated regressions. Exact quote matching remains provenance only: activation now additionally requires an operator-reviewed digest binding the full candidate, plus scope/type/source-authority validation.

Final command: `COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q` → **101 passed in 33.96s** (94 offline + 7 real FalkorDB integration). The offline command ` .venv/bin/python -m pytest -q` → **94 passed, 7 skipped in 0.35s**; skips do not count as integration success. Actual integration exercised native full paths, scoped database reads without revision JSON or Python traversal IDs, all four tools through MCP protocol, restricted public versus authorized coverage, 132 potential inventory-check evidence rows bounded to 1, persistence, read-only ACLs and publication failure. Clearance renewal and wrong-subject candidate regressions run offline; restricted coverage and budget tests additionally run on the actual engine.

The same actual-DB suite simulated UTC wallclock 30 days after the fixture assessment time. All 4 configured demo states matched explicit-time canonical results and goldens. Removing the demo-time setting restored real freshness and returned `needs_verification`. The readable current projection contains only eligible relations at ingestion's knowledge time; old projections use a historical label. Regression checks confirm the initial blocker/owner path and removal of the old invoice dependency after migration.

Three new clean replays:

```sh
COMPANY_BRAIN_LITE_PATH=/tmp/company-brain-stage7-corrections.rdb COMPANY_BRAIN_GRAPH=company_brain_demo_stage7_corrections COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python -m company_brain.replay --confirm-graph company_brain_demo_stage7_corrections --replays 3
```

Raw state counts: **3 resets, 12 assessments, 12/12 expected dispositions, 3/3 canonical-equality runs**. Each run returned `[blocked, blocked, needs_verification, no_known_blockers]`. Detailed evidence-linked output is regenerated at ignored `evals/results/replay.json`. Final logical inputs remain 11 entities, 20 source versions, 17 assertions and 1 declared inventory; the derived readable projection duplicates entities for inspection, not independent truth.

Local in-process assessment timing: n=12, min **6.735ms**, max/nearest-rank p95 **9.236ms**. Resets: **0.369, 0.261, 0.335ms**. Same Mac/Python/official FalkorDB 4.18.3 backend as above, engine defaults, no cache flush. These timings include scoped evidence reads, dynamic active resolution and graph traversal; exclude client inference, ingestion and MCP transport. They do not establish a database speed advantage or the MCP end-to-end latency target.

The sandboxed engine startup failed before test execution; the supported elevated run succeeded. No real model/client transcript, paid extraction or search benchmark was executed. Model, total spending cap and secure credential setup remain pending. Claude Desktop and Claude models are excluded by the user. Stage 7 remains under improvement; Stages 8/9, public push/visibility and deployment remain unapproved.

## Evaluation-preparation increment — 17 October 2026

Expanded full run: `COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q` → **110 passed in 35.80s** (102 offline, 8 actual-DB integration). This adds 8 offline evaluation/harness/golden tests and 1 actual-DB test to the correction increment's 101. Both additional question goldens passed on the same initial fixture graph: **2/2 cases, 15/15 required evidence mentions supported**, with required owner/blocker/decision support and `blocked` disposition preserved for the explicit scopes/times. Free-form model explanation quality remains unevaluated.

The comparison harness's actual-DB probe used a **scripted test double**, one graph assessment action and one search action followed by labeled scripted final messages. It verifies equal model configuration, immutable revision and record digest plumbing. It is not an LLM transcript, a benchmark outcome or evidence that search performs worse. The official MCP SDK protocol test separately exercises all four tools, server guidance and timezone validation.

See [raw preparation counts and fair-experiment controls](evaluation-preparation.md). No paid/live inference, model extraction accuracy, real-client conversations or comparative quality/latency/cost numbers are reported. Remaining gates are unchanged. The optional relationship ablation is not implemented.

## Final review follow-up

Full suite after partial-evidence citation consistency: **110 passed in 39.91s**. Tests now ensure returned nested permission IDs have retained evidence and returned workflows have retained supporting dependency paths. Budgets 1/4/8/12 are covered offline; the actual-DB native-path test checks a truncated budget-8 response. A final offline rerun after correcting default normalization in narrative scoring passed **102 tests, 8 integration skips in 0.35s**. The targeted final provider-neutral MCP protocol run also passed **1 test in 5.11s**.

Regenerating preparation revealed omitted `supersedes` was initially scored differently from default `[]`. The corrected scorer now normalizes that valid omission and has a regression. The regenerated available mock count is **1 expected, 1 proposed, 1 TP, 0 FP, 0 FN**. This does not establish model quality. Two other narrative records still have no model output.

Exact files changed since takeover baseline `7744a33`:

```text
README.md
data/raw_demo/manifest.json
docs/development/17-implementation-milestones.md
docs/development/18-local-development.md
docs/development/19-submission-plan.md
docs/planning/10-engineering-framework.md
evals/gold/narrative.json
evals/gold/questions.json
evals/results/evaluation-preparation.md
evals/results/verification.md
src/company_brain/assessment.py
src/company_brain/evaluation.py
src/company_brain/ingestion.py
src/company_brain/models.py
src/company_brain/server.py
src/company_brain/store.py
tests/test_assessment.py
tests/test_evaluation.py
tests/test_integration.py
tests/test_regressions.py
```

The complete actual main Cypher is reproduced verbatim in `README.md`, generated by `dependency_query(8)` from `src/company_brain/store.py`. Historical full revision JSON remains an operator ingestion/backup representation only; MCP assessment reads authorized scoped evidence rows, and all path expansion and active temporal/supersession resolution occur in FalkorDB.

Final-code replay rerun: **3/3 clean replays, 12/12 golden dispositions, canonical outputs identical across runs**. Each run returned `[blocked, blocked, needs_verification, no_known_blockers]`. Final local assessment samples n=12: min 6.704ms, max/nearest-rank p95 9.878ms; resets 0.392ms, 0.260ms, 0.289ms. Same hardware/runtime/cache limitations as above; no client inference.

## Rereview P1: baseline inventory and metadata authorization

The independent reviewer reproduced private inventory consumer IDs escaping through baseline `read_record`. Fixed whole-declaration authorization: omit an inventory if its service or any consumer is inaccessible, return generic incomplete coverage, never retain a filtered list labeled complete or leak the original count. Filter predecessor assertion IDs against the same accessible assertion set used by MCP history. Fully authorized callers retain the declarations and references. Source access is unchanged and matches MCP evidence.

Regression evidence: the three new offline cases failed before the fix (hidden consumer, hidden service, hidden predecessor ID), then all 11 evaluation tests passed in 0.15s. Full offline suite: **105 passed, 9 skipped in 0.37s**. Actual FalkorDB command:

```sh
COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests/test_integration.py::test_search_inventory_privacy_on_actual_graph /tmp/test_company_brain_rereview_db.py::test_search_does_not_leak_hidden_consumer_from_inventory
```

Result: **2 passed in 8.16s**. The repository actual-DB test covers public/authorized reads for both inaccessible consumers and inaccessible services, with no private names/IDs in returned search records or snippets. No model/API call or remote action occurred. Stage 7 remains under improvement.

## Rereview P2: scoped transitive supersession

Reproducer: usage ← original clearance (expires at noon) ← fresh renewal. The previous direct-only resolver discarded the expired intermediate before following its replacement link, so stale usage reappeared despite valid renewed clearance. Eight of the first sixteen offline lineage checks failed before the correction; the implemented policy and additional future-intermediate check now pass.

Semantics: resolve a currently eligible successor through at most 16 explicit same-subject/scope/revision links. Ignore **only intermediate end dates**; do not ignore approval, start dates, observed/recorded knowledge cutoffs, revocation or caller visibility. Candidate and suppressing successor still need their requested business interval. Inaccessible or revoked links are barriers; fully authorized callers can resolve accessible chains. No eligible renewal means expired clearance cannot grant clearance. A later renewal cannot fill a historical gap or rewrite an earlier knowledge view. Revoking source trust affects the new revision; retained earlier immutable revisions keep their prior state. Scope, subject and clearance target mismatches remain invalid. Ingestion rejects more than 16 links before publication rather than silently accepting a partially traversable chain.

Added regression coverage: **17 offline cases**, plus actual-DB matrices covering chain lengths 2/3/16, historical known-at and validity, seven barrier configurations (revoked leaf/intermediate, restricted leaf/intermediate, future-recorded leaf/intermediate, future-effective leaf), revocation with prior-revision preservation, and invalid scope/depth with unchanged published head. Restricted-case assertions check public responses and baseline metadata for absence of private IDs and confirm authorized resolution. Projection checks confirm the old reporting `RUNS_ON` edge stays out of the current view after renewal.

Final combined command:

```sh
COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests /tmp/test_company_brain_rereview_db.py
```

Result: **137 passed in 64.49s**. This comprises **122 offline + 12 repository actual-FalkorDB integration + 3 independent actual-DB tests**. The repository suite alone contains 134 tests. The separate final offline run passed **122 tests**, with 12 integration skips, in 0.43s. An earlier matrix attempt hit a test-fixture immutable-source identity collision before reaching its intended depth check; the corrected test setup now reaches the explicit depth rejection and verifies head preservation. No production failure was masked or skipped.

The independent file's renewal and inventory reproducers now pass, as does its three-reset/twelve-assessment canonical replay check. Full updated traversal statement: [`rereview-traversal.cypher`](rereview-traversal.cypher), generated verbatim by `dependency_query(8)` and reproduced in README. Inputs are revision, scope, epoch `planned`/`known`, trusted groups, target service and row budget. Supersession and dependency expansion remain in FalkorDB; no Python-derived traversal ID list is supplied.

P2 changed files: `src/company_brain/store.py`, `src/company_brain/ingestion.py`, `tests/test_assessment.py`, `tests/test_supersession.py`, `tests/test_integration.py`, `README.md`, `docs/development/18-local-development.md`, `docs/development/17-implementation-milestones.md`, this report, and `evals/results/rereview-traversal.cypher`. P1 is separately committed as `bdf661a`; its exact changed files are available in that commit.

No live/paid API, Claude use, public push, visibility change or deployment occurred. No new MCP tool was added. Live evaluation remains pending model selection, total spending cap and approved secure credential setup. Stage 7 and all subsequent human acceptance gates remain open.

Final standalone replay after the transitive-query change: **3/3 clean resets/runs, 12/12 golden dispositions, identical canonical outputs across runs**. Each run returned `[blocked, blocked, needs_verification, no_known_blockers]`. Local in-process assessment n=12: min 8.537ms; max/nearest-rank p95 35.116ms. Resets: 1.101ms, 0.321ms, 0.362ms. Engine defaults/no cache flush, same Mac and pinned backend; these exclude model inference and do not establish comparative or end-to-end performance. Detailed output is regenerated at ignored `evals/results/replay.json`.


## Authorized live synthetic round — 18 October 2026

The user approved exact OpenRouter model `openai/gpt-6-luna`, USD 3 total, and process-memory use of the existing ignored project credential. Implemented native API function calls with actual role=tool messages, matched graph/search controls, contextual raw-source extraction and a durable cross-attempt spending ledger. Removed an unsupported parallel_tool_calls parameter after the router rejected it; no Claude fallback was used. Earlier protocol failures and one timeout are preserved, not pooled into the latest cohort.

The latest paired cohort terminated all 12 arms: graph completed 6/6, search completed 3/6 and exhausted its equal tool budget in three. Graph matched all four retirement dispositions but had two citation-ID format errors; it failed the network-slip question after an unsuccessful broad entity lookup. Search's completed clear-state answer was conservative but wrong, and its extra question outputs failed structured fields/citation contracts. Narrative raw counts: 2 TP / 0 FP / 0 FN across three known synthetic records. Raw extraction: 13 records, 11 validations, two undated dependencies rejected, nine proposals, zero approved; actual raw graph remains needs_verification. These are exploratory results, not comparative performance, general model quality or human acceptance.

Full repository run passed 168 tests in 54.64s, including 12 actual-FalkorDB integration tests. Three fresh isolated real-DB replays passed 12/12 golden dispositions with identical canonical outputs. Then a report-only archive/resume correction added one test: final offline suite 157 passed, 12 integration skipped in 0.19s; focused budget suite 27 passed. It preserves old reports and removes inherited error/status from future resumed cohorts. The historical current raw artifact retains its stale top-level error, explicitly documented rather than rewritten.

Cumulative known receipts USD 0.021924765; one unresolved timeout retains USD 0.00468431250 allowance (ledger accounted USD 0.02660907750). Final read-only key usage USD 0.02273294, remaining USD 2.97726706, unchanged USD 3 limit. These overlapping figures must not be summed. See [full raw evidence and limits](live-2026-10-18/README.md). Stage 7 remains under improvement: retrieval robustness, exact answer/citation contracts, raw proposal approval, broader unseen scenarios and provider-neutral external MCP client validation remain open. No subsequent framework gate, publication, push or deployment is approved.

## Retrieval/citation correction checkpoint

On dev, the harness now bounds empty-result decomposition guidance and premature-final repair, separates assertion/source references, and validates exact retrieved workflow/decision IDs, ownership references and assessment disposition. Both arms share the policy and bounded repairs; original scores are retained. Reference validation is not semantic answer grading. See the development milestone and upcoming separate v4 evidence for outcomes.

`COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest -q tests`: **191 passed in 57.93s**, including **13 actual-FalkorDB integration tests**. Focused evaluator/budget checks: **59 passed**. Three fresh actual-DB replays: **3/3 runs, 12/12 golden dispositions**, identical canonical outputs, `[blocked, blocked, needs_verification, no_known_blockers]`. No query, freshness rule, authority review or golden was loosened.
