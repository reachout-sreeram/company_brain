# Recorded live proposals → selected review → graph change

Tested implementation: **985f0c7**. This is synthetic demonstration reviewer activity, not a real person's approval or framework acceptance. Inference and review are separate: the recorded Luna run yielded 11 unapproved proposals from 13 validated source records. Four were inspected against their full source text, identity, scope, temporal metadata and quote spans; seven remain unapproved. Nothing is approved through MCP.

## Ready recording command

From the repository root, use a fresh directory:

```sh
.venv/bin/python presentation-assets/reviewed-demo/replay_approval.py --output .local/recording-review-1
```

No API key or paid call is used. The script starts its own real FalkorDBLite, runs the actual CLI steps below and prints actual revisions/dispositions. It never resets the evaluation graph. Existing output directories are refused. The action uses the current review time, preserving historical source observation times and real freshness rules. If replayed long after the October fixture window, inspect the recorded proof instead of pretending the historical observations are fresh.

The script records every actual CLI argv/result in `proof.json`. Open `candidates.json`, `before.json`, `approval.json`, `review-history.json`, `after.json` and `before-review-knowledge.json` for individual scenes. [Recorded original proof](recorded-proof/proof.json), [pending proposals](pending.json), [approved bundle with retained proposals/audit](recorded-proof/reviewed.json).

## Exact selected IDs and command

Only these four frozen candidates are selected, after source validation:

| Proposal | Source/version | Fact checked |
|---|---|---|
| extract-e1439acc053738b33e07aeb4 | source-run-invoice-legacy@1 | invoice-export runs on legacy-runner, explicitly observed 17 October 09:00 UTC |
| extract-ed1de0ddfaf3e889e164c98b | source-requires-billing-invoice@2 | billing requires invoice export; explicitly declared prerequisite validity, not runtime observation |
| extract-82af5c14e512875540990c30 | source-owns-invoice@1 | roster assigns invoice export to data-platform |
| extract-1f030345bfd89a795d1be50c | source-permits-invoice@1 | temporary-exception permits use through 1 November 00:00 UTC, exclusively |

The operator approval command executed inside the isolated script is equivalent to:

```sh
.venv/bin/company-brain approve-proposals presentation-assets/reviewed-demo/pending.json \
  --proposal extract-e1439acc053738b33e07aeb4 \
  --proposal extract-ed1de0ddfaf3e889e164c98b \
  --proposal extract-82af5c14e512875540990c30 \
  --proposal extract-1f030345bfd89a795d1be50c \
  --actor demo:synthetic-source-validation --demonstration \
  --reviewed-at REVIEW_ACTION_TIME_WITH_TIMEZONE \
  --note 'Synthetic demonstration: full selected candidates checked against source; not human acceptance.' \
  --output FRESH_OUTPUT/reviewed.json
```

Before that it runs `proposals` and `ingest pending.json`; afterward it runs `review-history`, `ingest reviewed.json` and `assess` with the same scope/planned/known time as the before answer. The script supplies the actual timezone-aware review-action time and the longer full review note; recorded argv preserves every argument. Both approval time and approval kind are visible in evidence. No original proposal/source is overwritten, no model output is approved as a batch, and no observation time is synthesized.

## Verified change

At **2026-10-18T06:48:16.904275+00:00**, review `review-24fcc90b59157bfd1611712b`:

- Before revision `6015beebb2f52e59a1f4bb00d77a91bfc3e8395e9de5c6d7f5c2a9a533d83f13`: **needs_verification**.
- After revision `41bb695c873ee9d21ee7eac86ef5020a3e2c42bdc5a94b125aa8be530eb0046b`: **blocked**, with billing impact, export ownership and the finite permission supported by approved evidence.
- Earlier knowledge at the reviewed revision remains **needs_verification**; approval is not retroactive.
- Four approved copies reference the retained proposal IDs and audit event; seven remain proposals. Missing migration-tracking extraction is not invented, and this partial graph is not represented as complete company coverage.

A second isolated handoff check also passed using a restricted child environment and fresh current review timestamp. This script/data is ready for recording; it is not itself a recorded video. Release, desktop-client recording and submission remain with the user/other recording agent.

## External read-only MCP client handoff

After the replay finishes, its real database persists at `FRESH_OUTPUT/demo.rdb`. An external recording agent can use the absolute `.venv/bin/company-brain-mcp` executable with:

```text
COMPANY_BRAIN_LITE_PATH=ABSOLUTE_FRESH_OUTPUT/demo.rdb
COMPANY_BRAIN_GRAPH=company_brain_demo_reviewed_narrative
COMPANY_BRAIN_KNOWN_AT=reviewed_at from FRESH_OUTPUT/proof.json
```

Use that same reviewed_at as planned_at for the before/after question, with scope production/eu. The recorded example is `2026-10-18T06:48:16.904275+00:00`; a new replay has its own actual timestamp in proof.json. Do **not** pin this newly approved graph to 17 October: that deliberately selects a knowledge view before approval and correctly leaves the claims inactive. The separate seeded four-state demo continues to use its 17 October time. No desktop configuration or recording is performed by this handoff, and the client still has only read tools.
