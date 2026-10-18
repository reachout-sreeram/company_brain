# Live Luna → MCP demonstration

Actual model: `openai/gpt-6-luna`, through OpenRouter with OpenAI-only routing,
no fallback, price fences, and no automatic retries. The model selected native
functions; the host executed their arguments using official MCP SDK `call_tool`
over an initialized stdio subprocess connected to a separate real temporary
FalkorDBLite graph. No direct Python domain calls answered model-selected tools.
Only bootstrap ingestion uses the operator store to seed synthetic fixtures.

This is an actual custom model/SDK client, **not** Codex desktop or Claude.

## Outcome and limitations

**Latest authorized exact-contract rerun passed**, with strict native-function
schema enforcement, one final attempt, no validation errors and no feedback
repair. Four new model responses selected all four actual MCP tools. The final
permission object uses the exact `until` field. The final answer is reproduced
without changes in `LUNA-RESULT.md`; the raw transcript is `luna-transcript.json`.

The generic client schema now declares and requires every permission property
(`decision_id`, `assertion_id`, `until`) and forbids extras. Closed schemas cover
the remaining final output too. The host validates both schema and equality to
actual retrieved evidence; it never renames or fixes a model answer after output.
At most one bounded feedback repair was available, but unused. Independent native
tool batches are executed sequentially over MCP and normalized into single-call
message pairs for the existing guarded adapter; original native batches remain
in receipts. No MCP arguments or final values are rewritten.

The final conversation used `find_entities`, `assess_retirement`, `get_evidence`
and `get_history`. Luna preserved the blocked disposition, both conflicts, all
five coverage gaps, truncation=false, and the temporary exception expiry. All 13
final citation IDs/source IDs/versions/quotes match its actual assessment response.
The exception source version was fetched with `span_id=null`; the matching
`get_history` assertion supplied start/end/quote. Post-run reconciliation checked
the exact source substring against those actual tool results. The live client
did not independently fetch all 13 source spans;
the earlier scripted protocol demo did so for its own pinned fixture/code state.

**The earlier final validation failed and remains preserved.** Luna returned the exception's expiry under
`effective_until` and added `permits_consumer_id`, while the host required a literal
copy of the assessment permission object with `until`. The actual expiry value
is unchanged. Original status `failed_contract_checks` and the untouched model
answer remain byte-for-byte in `luna-pre-exact-transcript.json` and
`LUNA-PRE-EXACT-RESULT.md`. The old structural review is retained in
`luna-pre-exact-reconciliation.json`; it does not promote the
failed contract result to a pass or prove every prose claim semantically.

The exact natural-language question, host prompt, MCP instructions, native tool
schemas, assistant tool choices, real tool responses, and final answer are recorded.
`LUNA-RESULT.md` reproduces the actual model explanation and final JSON without
rewriting them. Prompts require a historical knowledge date for reproducibility;
this is not a current production assessment or shutdown approval.

## Preserved failures and continuation

1. Attempt 1: Luna used lowercase `kind="service"`; exact and shorter searches
   all returned empty. It declined to assess. Four responses cost USD 0.000585425.
   Preserved in `luna-attempt1-{transcript,receipts}.json`.
2. Attempt 2: host guidance explained case-sensitive `Service`. Luna resolved the
   service, assessed it, then selected `get_evidence` and `get_history` together.
   The existing host's one-function-per-message restriction stopped before that
   batch ran. Three responses cost USD 0.000858200. Preserved in
   `luna-attempt2-{transcript,receipts}.json`.
3. The host resumed those already-paid recorded tool choices against a fresh
   isolated database with the exact same graph revision, using actual MCP calls.
   For the existing guarded adapter's single-call message contract, the original
   two-call assistant response was normalized into sequential assistant-call/tool-
   result pairs; original native response remains in attempt 2 receipts. No model
   call regenerated that batch. One subsequent response cost USD 0.000826580 and
   produced the final answer with the strict permission-field mismatch above.
4. Parent explicitly authorized one exact-contract rerun. The generic strict
   schema and nine local regression tests were added in this isolated directory.
   The rerun passed without repair: four responses, four MCP tools, USD 0.001729835.
   The exact-contract rerun is guarded against repetition. No further retry ran.

## Budget and receipts

All twelve receipts report `openai/gpt-6-luna`. Previously reported cost:
USD 0.002270205. **New incremental cost: USD 0.001729835. Cumulative actual worker
cost: USD 0.004000040**; conservative/unknown charges: **0**; open reservations: **0**.
This is cumulative across both attempts and the batch resume, under the parent's
USD 0.10 allocation and USD 3 total authorization. Add only the **new incremental
cost** if the prior USD 0.002270205 has already been reconciled. The shared implementation ledger was
read for the initial allowance check and never modified. Per-response IDs, token
usage and costs are in the four receipt files and `luna-reconciliation.json`.
`luna-budget.json` is the separate durable worker ledger; do not delete/reset it.

Per attempt limits: 12 model responses, 10 MCP calls, 4000 output tokens per model
response, 65536-byte context ceiling, one provider attempt per response. Actual
worker usage: twelve model responses total; attempt 1 three MCP lookup calls;
attempt 2/resume four successful MCP calls; exact-contract rerun four successful
MCP calls. No uncertain request was retried.

## Commands executed

From `company-brain/`, using existing dependencies and the named ignored project
credential loaded only into process memory:

```sh
COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python presentation-assets/mcp-client-demo/luna_client.py --execute-approved-usd010
COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python presentation-assets/mcp-client-demo/luna_client.py --execute-approved-usd010 --continue-after-reviewed-failure
COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python presentation-assets/mcp-client-demo/luna_client.py --execute-approved-usd010 --resume-pending-parallel-calls
COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python presentation-assets/mcp-client-demo/luna_client.py --execute-approved-usd010 --rerun-exact-contract-once
```

These document the completed run. Existing ledger/archive guards prevent silently
repeating it. A future paid run needs explicit coordination and a preserved cost
history, not deletion of guards. Local process/socket and outbound API permissions
were granted through execution escalation. No installs, persistent credentials,
client configuration, source/evaluation edits, commits or pushes were performed.

Offline regression command, from `company-brain/`:

```sh
.venv/bin/python -m pytest presentation-assets/mcp-client-demo/test_luna_client.py -q
```

Result: **9 passed**. Tests use retained actual tool responses, including the
original renamed-field failure. Offline positive controls construct expected
inputs only; they never replace a live model output. Covered regressions include
expiry, disposition, gaps, quote, duplicate citations and extra permission fields.
