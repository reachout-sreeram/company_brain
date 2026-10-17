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
