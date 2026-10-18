# Company Brain — three-minute recording handoff

Tested core: **985f0c7**. The user/recording agent owns video, release and submission. This is a script, not evidence that a video exists. Show actual outputs; the review actor is explicitly a synthetic demonstration, not a real human approval.

| Time | Show | Say |
|---|---|---|
| 0:00–0:25 | Architecture; billing → invoice export → legacy-runner | “Can we retire an old service without breaking billing? A completed ticket cannot answer that alone. Company Brain connects company records in real FalkorDB and follows business dependencies, blockers, owners and exceptions back to source evidence.” |
| 0:25–0:55 | Initial result and recorded MCP source inspection | “Billing requires invoice export on the old runner. Data Platform owns the export; Security owns the network approval blocking migration. A temporary exception permits use until November first. That is permission to keep using it, not evidence of migration or shutdown approval. Four read-only MCP tools expose the assessment and exact source spans.” |
| 0:55–1:15 | Four-state replay strip | “Ticket completion still leaves retirement blocked because runtime evidence conflicts. Verified invoice migration removes billing impact, but reporting still needs verification. Only fresh, scoped reporting verification closes that gap: blocked, blocked, needs verification, no known blockers.” |
| 1:15–2:10 | reviewed-demo pending/candidates/before/approval/after JSON | “Now these recorded live narrative proposals enter a separate graph. Their exact quotes pass validation, but proposals alone stay inactive. We inspect four candidates: runtime, billing prerequisite, owner and dated exception. This is a clearly labeled synthetic reviewer action. The CLI records actor, time, full digests and source versions, retaining every original proposal. After publication the same question changes from needs verification to blocked, with billing impact. Seven proposals remain unapproved. Looking back before the review still shows needs verification.” |
| 2:10–2:30 | Exact native Cypher and audit edges | “FalkorDB resolves temporal eligibility, source visibility, reviewed approval time and supersession, then returns bounded full paths. Python assembles policy and evidence. There is no Python BFS or precomputed traversal list, and no MCP tool can approve facts or change infrastructure.” |
| 2:30–3:00 | Final report, tests, raw failures and client evidence | “The tested core passed 229 checks, including fifteen real-database tests. The final known synthetic comparison completed twelve arms: graph dispositions matched six of six, search four of six. Host fidelity checks and repairs are part of those results, not proof of general superiority. Extraction still missed a relationship and misdated a completion claim; neither was silently approved. Codex assisted the implementation, fixtures, tests and documentation.” |

## Tested operator scene

From company-brain/, choose a fresh output directory:

```sh
.venv/bin/python presentation-assets/reviewed-demo/replay_approval.py --output .local/recording-review-1
```

It uses actual FalkorDBLite and the real CLI, not a mocked answer. No paid call or key is needed. [Selected IDs, exact approval command and recorded before/after revisions](../../presentation-assets/reviewed-demo/README.md). For individual scene control, use the captured CLI argv in `recorded-proof/proof.json`; the replay wrapper manages an isolated database and produces separate scene files. Do not claim that this partial live-derived graph is the fully seeded four-state graph or that it demonstrates shutdown clearance.

For the seeded replay scene:

```sh
COMPANY_BRAIN_LITE_PATH="$PWD/.local/video-replay.rdb" COMPANY_BRAIN_GRAPH=company_brain_demo_video COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python -m company_brain.replay --confirm-graph company_brain_demo_video --replays 3
```

This explicitly resets only the named demo graph. Use the historical demo time for seeded facts; do not silently present stale observations as current. [Current-schema SDK stdio evidence](../../presentation-assets/mcp-client-demo/current-schema/protocol-transcript.json) is scripted protocol verification. [Live Luna through actual MCP](../../presentation-assets/mcp-client-demo/LUNA-DEMO.md) is a CLI agent, not a desktop UI. Preserve its failed earlier attempts as separate evidence. Any separate desktop recording must retain the graph disposition, gaps, conflicts, exception expiry and citations; no write tool or approval by MCP is claimed.

## Claims to retain

The narrative source dates are synthetic historical data. The prerequisite interval is explicit operator-declared metadata, not a runtime observation. The review is a demonstration action, not participant acceptance. `no_known_blockers` is scoped evidence status, never authorization. There is no production/company connector, scale benchmark, deployment, finished video or submission implied by these artifacts. Release readiness and the official checklist are in README; they remain user-owned pending actions.
