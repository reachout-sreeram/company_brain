# Evaluation preparation — no live benchmark

Generated with `.venv/bin/python -m company_brain.evaluation --prepare-only`.
No provider runtime, credentials or model calls are used. Counts below describe
synthetic inputs, manually authored goldens and one existing deterministic mock;
they do not measure model extraction accuracy or graph-versus-search improvement.

## Raw input and preparation counts

```json
{
  "states": [
    {
      "state": "initial",
      "entities": 11,
      "source_versions": 13,
      "assertions": 12,
      "inventories": 1
    },
    {
      "state": "completion",
      "entities": 11,
      "source_versions": 15,
      "assertions": 13,
      "inventories": 1
    },
    {
      "state": "migration",
      "entities": 11,
      "source_versions": 18,
      "assertions": 16,
      "inventories": 1
    },
    {
      "state": "clear",
      "entities": 11,
      "source_versions": 20,
      "assertions": 17,
      "inventories": 1
    }
  ],
  "counts": {
    "inference_calls": 0,
    "provider_requests": 0,
    "live_benchmark_runs": 0,
    "real_client_transcripts": 0,
    "question_goldens": 2,
    "required_question_evidence_mentions": 15,
    "narrative_gold_records": 3,
    "narrative_expected_facts": 2,
    "mock_covered_records": 1,
    "unevaluated_narrative_records": 2
  },
  "available_mock_narrative_scores": [
    {
      "source_key": "source-permits-invoice@1",
      "expected": 1,
      "proposed": 1,
      "true_positive": 1,
      "false_positive": 0,
      "false_negative": 0
    }
  ]
}
```

## Same-record, same-model experiment

`Toolbox` constructs the search arm from exactly the caller-authorized, scoped
source versions, reviewed assertions and inventories at the graph revision.
Search can rank keywords and explicit identifiers, page results, and read complete
records with metadata, assertions and inventory declarations. It can follow
references iteratively. It has no relationship expansion and is not an MCP tool.
Both arms may inspect dated historical/future records; shared policy restricts
what may support an assessment known at the requested time.

`run_pair` uses one frozen `Experiment`: identical model ID, temperature (0),
output cap (4096 tokens), 20 turns, 12 tool calls and 65536 serialized context
bytes for each arm. Context counts include tool descriptions and messages.
Records digest, graph revision, tool events, calls and context bytes are retained.
A changed revision aborts; budget exhaustion is not a completed result. Randomize
or counterbalance order over real repetitions and use a stateless client adapter.
Source order/record IDs, caller, scope, planned_at and known_at must also match.
No gold answer is supplied to either arm. A graph response may not be overridden.

The provider-neutral client interface accepts a single structured tool action or
final answer per step. No live inference adapter is supplied or invoked. Automated
scripted harness probes are explicitly test doubles, not model/client transcripts.
The official MCP protocol tests separately exercise the four server tools.

## Scoring and execution gates

`score_answer` reports raw required/correct evidence, unsupported citations,
workflow/blocker/owner/decision counts, disposition correctness and gap reporting.
Citations must have appeared in returned tool support; a keyword snippet alone
does not establish assertion support. Independently review prose entailment,
unsupported causal claims, conflicts and exception expiry; counts alone do not
prove correct explanations. Record token usage, provider-reported dollar cost,
model/endpoint configuration, tool latency and end-to-end latency separately in
an eventual real run. The current harness does not enforce a dollar budget.

`score_narrative` checks exact subject, predicate, object/value, target, scope,
effective dates and supersession with duplicate-aware TP/FP/FN counts. Normal
candidate validation additionally checks timestamps and exact source spans.
The completion claim and injection records have manual expectations but no model
output yet. A matching curated mock is not a model extraction result. Operator
review is still required before activation; a gold file cannot grant trust.

Remaining gates: selected non-Claude model, approved total spending cap and secure
credential setup before any paid/live execution; no secrets in chat. Search
comparison and narrative inference are unexecuted. Relationship ablation is
optional and not implemented. No benchmark or user-savings claim is established.

Two additional question goldens reuse the initial graph and existing records:
`evals/gold/questions.json`. The billing slip answer is conditional: a week later
is 24 October, inside the permission interval ending 1 November. Continued use
may be permitted; the records do not establish a billing outage, deadline or
successful future migration. Actual graph support is checked in integration.
