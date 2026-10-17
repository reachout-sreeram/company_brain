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
